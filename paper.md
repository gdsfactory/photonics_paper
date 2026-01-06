---
title: GDSFactory
subtitle: The open ecosystem for EPIC design.
short_title: GDSFactory
description: In this short tutorial we provide an overview how GDSFactory bridges (or unifies?) the full EPIC design cycle.
license:
  content: CC-BY-SA-3.0
keywords:
    - Integrated Photonics
    - GDSII
    - Python
    - electronic design automation (EDA)
export:
  - format: pdf
    template: ./util/lapreprint-typst

kernelspec:
  name: python3
  display_name: 'Python 3'
---

# Abstract
Designing an EPIC -- and (electronic) photonic integrated circuit -- requires robust tooling ranging from exploratory simulation via mask layout and verification to validation. In the past a variety of specialized syntaxes were introduced with similar tooling for electronic chip design -- the older cousin of EPICs. The relatively young age of integrated photonics opens up the opportunity to establish an accessible workflow which is intuitive, easily customizeable and extensible. GDSFactory is a Python based framework to build EPICs that provides a common syntax for design/layout, simulation (Ansys Lumerical, tidy3d, MEEP, MPB, DEVSIM, SAX, Elmer, Palace, …), verification (Klayout DRC, LVS, netlist extraction, connectivity checks, fabrication models) and validation. This paper showcases the capabilities of GDSFactory, highlighting its end-to-end workflow, which enables users to turn their chip designs into working products.

# Introduction
Hardware iterations typically require months of time and involve substantial financial investments, often in the millions of dollars. In contrast, software iterations can be completed within hours and at a significantly lower cost, typically in the hundreds of dollars. Recognizing this discrepancy, GDSFactory aims to bridge the gap by leveraging the advantages of software workflows in the context of hardware chip development.

To achieve this, GDSFactory offers a comprehensive solution through a unified Python API. This API enables users to drive various aspects of the chip development process, including layout design, verification (such as optimization, simulation, and design rule checking), and validation (through the implementation of test protocols). By consolidating these functionalities into a single interface, GDSFactory streamlines the workflow and enhances the efficiency of hardware chip development.

```{raw:typst}
#set page(margin: auto)
```

```{figure} figures/DesignCycle.png
:scale: 80 %
:alt: Closing the design cycle with GDSFactory.

GDSFactory bridges the whole EPIC design cycle, with a variety of Foundary PDKs available it is both easy to construct circuits reusing proven devices and to realize conceptually new designs. The generated component layouts can be used in varous simulators for exploration, optimization and validation. GDSfactory tightly integrates with KLayout, leveraging its advanced design rule checks (DRC) and layout versus schematic (LVS) capabilities. For characterization of the fabricated devices GDSFactory provides rich metadata compatible to commercial wafer probers, including the position and orientation of fiber-to-waveguide couplers.
```

With GDSFactory you can:
- Design (Layout, Simulation, Optimization)
    - Capture design intent in a schematic and automatically generate a layout.
    - Define parametric cells (PCells) functions in python or YAML. Define routes between component ports.
    - Test component settings, ports and geometry to avoid unwanted regressions.
- Verify (DRC, DFM, LVS)
    - Run simulations directly from the layout thanks to the simulation interfaces. No need to draw the geometry more than once.
        - Run Component simulations (EM solver, FDTD, EME, TCAD, thermal …)
        - Run Circuit simulations from the Component netlist (Sparameters, Spice)
        - Build Component models and study Design For Manufacturing.
    - Create DRC rule decks.
    - Make sure complex layouts match their design intent (Layout Versus Schematic).
- Validate
    - Make sure that as you define the layout you define the test sequence, so when the chips come back you already know how to test them.
    - Model extraction: extract the important parameters for each component.
    - Build a data pipeline from raw data, to structured data and dashboards for monitoring your chip performance.

# Design Flow

GDSFactory offers a range of design capabilities, including layout description, optimization, and simulation. It allows users to define parametric cells (PCells) in Python, facilitating the creation of complex components. The library supports the simulation of components using different solvers, such as finite element mesh, mode solver (finite element, finite difference time domain, finite different Bloch mode solver), TCAD and thermal simulators, and FDTD simulations. Optimization capabilities are also available through an integration with Ray Tune, enabling efficient parameter tuning for improved performance.
As input, GDSFactory supports 3 different workflows that can be also mixed and matched.

1. Write python code. Recommended for developing cell libraries.
2. Write YAML code to describe your circuit. Recommended for circuit design. Notice that the YAML includes schematic information (instances and routes) as well as Layout information (placements).
3. Define schematic, export SPICE netlist, convert SPICE to YAML and tweak YAML.

As output you write a GDSII or OASIS file that you can send to your foundry for fabrication. It also exports component settings (for measurement and data analysis) and netlists (for circuit simulations). The following examples concentrate on photonic integrated design, however they are readily adaptable for RF and analog circuit design.

## Parametric Cells (PCells) in Python or YAML
A PCell is a Parametric Cell describing the geometry of a particular device. PCells can accept other PCells as arguments in order to build arbitrarily complex Components.

:::{code-cell} python
:label: compositing
:caption: Creating a new `component` by composition of a Mach-Zehnder interferometer  and a bent waveguide attached at port `o2`.

import gdsfactory as gf

@gf.cell
def mzi_with_bend(radius: float=10)->gf.Component:
    c = gf.Component()
    mzi  = c << gf.components.mzi()
    bend = c << gf.components.bend_euler(radius=radius)
    bend.connect('o1', mzi['o2'])
    c.add_port('o1', port=mzi['o1'])
    c.add_port('o2', port=bend['o2'])
    return c

c = mzi_with_bend(radius=20)
c.plot()
:::

[](#compositing) demonstrates how a new PCell can be created by composing PCells defined prior. Connecting port `o1` of the bend to `o2` of the MZI ensures their correct relative placement, respecting the orientation of the optical ports.

Manually routing complex circuits quickly becomes cumbersome. To alleviate this burden GDSFactory provides a routing API for (semi-)automatic waveguide routing. Given a declarative description of the desired connections it can create single and bundled waveguide routes, that avoid obstacles and collisions between the bundled waveguides. A minimal demonstration of the routing API is provided in [](#routing).

:::{code-cell} python
:label: routing
:caption: Connecting components via single waveguide or bundles can be automated using the routing API.

@gf.cell
def nxn_to_nxn() -> gf.Component:
    c = gf.Component()
    c1 = c << gf.components.nxn(east=3, ysize=20)
    c2 = c << gf.components.nxn(west=3)
    c2.move((40, 10))
    gf.routing.route_bundle_sbend(
        c,
        c1.ports.filter(orientation=0),
        c2.ports.filter(orientation=180),
        sort_ports=True,
        cross_section="strip",
    )
    return c

c = nxn_to_nxn()
c.plot()
:::

While defining PCells in python is very powerfull, one commonly simply desires to combine pre-existing building block into circuits (as in [](#compositing) and [](#routing)). In these cases it can be beneficial to describe the desired circuit in a netlist-like format. For this purpose GDSFactory establishes a YAML based representation. The specification equivalent to [](#routing) is shown in [](#yaml). 

:::{code-block} yaml
:label: yaml
:caption: When composing circuits it is often more convenient to define subcomponents and their relative position in the YAML based design flow. The given example yields the same layout as [](#routing)

name: nxn_to_nxn
instances:
  c1:
    component: nxn
    settings:
      east: 3
      ysize: 20
  c2:
    component: nxn
    settings:
      west: 3
placements:
  c2:
    x: 40
    y: 10
routes:
  optical:
    routing_strategy: route_bundle_sbend
    links:
      - c1,o4: c2,o1
      - c1,o3: c2,o2
      - c1,o2: c2,o0
:::

## Schematic Driven Layout
For complex circuits you can start with a Schematic view that you can convert to YAML.

## Simulations directly from Layout
The GDSFactory ecosystem supports multiple solvers to simulate the physical behavior of the created design. These cover several aspects, like the optical behavior of single components via finite difference time domain simulations, the collective behavior of multiple coupled components via scattering matrix (S-matrix) circuit simulators, the propagation of thermal transients, electronic properties and more. The single source of truth providing the device geometry, is a key benefit of GDSFactory linking these different simulators together.



# Conclusion
The paper has highlighted the key features and functionalities of GDSFactory for hardware design. By leveraging the power of Python, GDSFactory empowers designers with a familiar and flexible programming language widely used in machine learning, scientific computing, and engineering. This enables seamless integration with existing software ecosystems and promotes code reuse and collaboration.

The verification and validation capabilities of GDSFactory play a crucial role in ensuring the manufacturability and functionality of the designed chips. From functional verification to design for robustness and manufacturing, GDSFactory offers tools and methods to design chips, detect potential issues, and optimize performance.

Furthermore, GDSFactory provides an interactive schematic capture feature that enhances the design process and facilitates the alignment between design intent and the produced layout. With support for SPICE and YAML, designers have the flexibility to define and modify schematics in a user-friendly manner, either visually or programmatically.

The ability to define test sequences and measurement parameters within GDSFactory streamlines the post-fabrication testing process. By establishing a clear measurement and data analysis pipeline, designers can evaluate the fabricated components against the design specifications, ensuring the delivery of known good dies. In conclusion, GDSFactory is a comprehensive and extensible design automation tool that empowers designers to efficiently develop integrated circuits and components. Its Python-driven workflow, combined with its integration capabilities, verification tools, schematic capture feature, and test sequence definition, provides a powerful platform for turning chip designs into validated products. 

# Acknowledgements
We would like to acknowledge all other contributors to the GDSFactory project who at the time of writing are: Simon Bilodeau (Google), Niko Savola (Google, Aalto University), Marc de Cea Falco (Google), Helge Gehring (Google), Yannick Augenstein (FlexCompute), Ryan Camacho (BYU), Sequoia Ploeg (BYU), Prof. Lukas Chrostowski (UBC), Erman Timurdogan (Lumentum), Damien Bonneau (PsiQuantum), Alec Hammond (Meta), Thomas Dorch (HyperLight), Alex Sludds (Lightmatter), Igal Bayn (Quantum Transistors), Skandan Chandrasekar (UWaterloo), Tim Ansell, Ardavan Oskoii (Meta), Bradley Snyder (Superlight) and Amro Tork (Mabrains). Erman Timurdogan contributed the GDSFactory design, verification and validation cycles figure and Dario Quintero contributed the GDSFactory microservices architecture figure.

We would also like to acknowledge the foundational work of other open-source developers: Adam McCaughan (PHIDL), Juan Sanchez (DEVSIM),  Matthias Köfferlein (Klayout), Ardavan Oskooi, Alec Hammond, Stephen Johnson (MEEP), Jesse Lu (FDTDZ), Dan Fritchman (VLSIR), Dario Quintero (PIEL), Floris Laporte (SAX, MEOW). 

# Availability
The source code of GDSFactory is available publicly on [github](https://github.com/gdsfactory/gdsfactory) under MIT license. The demonstrations presented here can be run interactively in the [online version of this paper](https://github.com/gdsfactory/photonics-paper). Similarly an extensive [documentation](https://gdsfactory.github.io/gdsfactory/) including further examples and a full overview of the API is available.
