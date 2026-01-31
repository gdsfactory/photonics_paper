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
    output: exports/paper.pdf
    id: pdf-export

downloads:
  - id: pdf-export
    title: A PDF of this document

kernelspec:
  name: python3
  display_name: 'Python 3'
---

# Abstract
Designing an EPIC -- and (electronic) photonic integrated circuit -- requires robust tooling ranging from exploratory simulation via mask layout and verification to validation. In the past a variety of specialized syntaxes were introduced with similar tooling for electronic chip design -- the older cousin of EPICs. The relatively young age of integrated photonics opens up the opportunity to establish an accessible workflow which is intuitive, easily customizeable and extensible. GDSFactory is a `python` based framework to build EPICs that provides a common syntax for design/layout, simulation (Ansys Lumerical, tidy3d, MEEP, MPB, DEVSIM, SAX, Elmer, Palace, …), verification (Klayout DRC, LVS, netlist extraction, connectivity checks, fabrication models) and validation. This paper showcases the capabilities of GDSFactory, highlighting its end-to-end workflow, which enables users to turn their chip designs into working products.

# Introduction
Hardware iterations typically require months of time and involve substantial financial investments, often in the millions of dollars. In contrast, software iterations can be completed within hours and at a significantly lower cost, typically in the hundreds of dollars. Recognizing this discrepancy, GDSFactory aims to bridge the gap by leveraging the advantages of software workflows in the context of hardware chip development.

To achieve this, GDSFactory offers a comprehensive solution through a unified `python` API. This API enables users to drive various aspects of the chip development process, including layout design, verification (such as optimization, simulation, and design rule checking), and validation (through the implementation of test protocols). By consolidating these functionalities into a single interface, GDSFactory streamlines the workflow and enhances the efficiency of hardware chip development.

```{raw:typst}
#set page(margin: auto)
```

```{figure} figures/DesignCycle.png
:alt: Closing the design cycle with GDSFactory.

GDSFactory bridges the whole EPIC design cycle, with a variety of Foundary PDKs available it is both easy to construct circuits reusing proven devices and to realize conceptually new designs. The generated component layouts can be used in varous simulators for exploration, optimization and validation. GDSfactory tightly integrates with KLayout, leveraging its advanced design rule checks (DRC) and layout versus schematic (LVS) capabilities. For characterization of the fabricated devices GDSFactory provides rich metadata compatible to commercial wafer probers, including the position and orientation of fiber-to-waveguide couplers.
```

GDSFactory acts a as a unifying framework that covers the entire EPIC design cycle. It allows the user to:

- Design (Layout, Simulation, Optimization)
    - Capture design intent in a schematic and automatically generate a layout.
    - Define parametric cells (PCells) functions in `python` or `YAML`. Define routes between component ports.
    - Test component settings, ports and geometry to avoid unwanted regressions.
- Verify (DRC, DFM, LVS)
    - Run simulations directly from the layout thanks to the simulation interfaces. No need to draw the geometry more than once.
        - Run Component simulations (EM solver, FDTD, EME, TCAD, thermal …)
        - Run Circuit simulations from the Component netlist (Sparameters, Spice)
        - Build Component models and study Design For Manufacturing.
    - Create DRC rule decks.
    - Make sure complex layouts match their design intent (Layout Versus Schematic).
- Measure and Validate
    - Make sure that as you define the layout you define the test sequence, so when the chips come back you already know how to test them.
    - Model extraction: extract the important parameters for each component.
    - Build a data pipeline from raw data, to structured data and dashboards for monitoring your chip performance.

In this paper we will highlight the key features of GDSFactory follwing the structure of the design cycle shown in Figure 1 and  mentioned above.

# Design Flow

GDSFactory offers a range of design capabilities, including layout description, optimization, and simulation. It allows users to define parametric cells (PCells) in `python`, facilitating the creation of complex components. The library supports the simulation of components using different solvers, such as mode solvers (finite element and finite difference eigenmode solvers), eigenmode expansion methods (EME), TCAD and thermal simulators, and fullwave FDTD simulations. Optimization capabilities are also available through an integration with Ray Tune, and automatically differentiable solvers enabling efficient parameter tuning for improved performance.

## Mask Layout
Generating mask layouts ready for fabrication is the core functionality of GDSFactory.
As input, GDSFactory supports 3 different workflows that can be also mixed and matched.

1. Write `python` code. Recommended for developing cell libraries.
2. Write `YAML` code to describe your circuit. Recommended for circuit design. Notice that the `YAML` includes schematic information (instances and routes) as well as Layout information (placements).
3. Define schematic, export SPICE netlist, convert SPICE to `YAML` and tweak `YAML`.

As output you write a GDSII or OASIS file that you can send to your foundry for fabrication. It also exports component settings (for measurement and data analysis) and netlists (for circuit simulations). The following examples concentrate on photonic integrated design, however they are readily adaptable for RF and analog circuit design.

<!-- TODO: align examples to form one cohesive storyline: e.g. layout e.g. strip to slot converter; slot modulator; PIC -->
:::{side-by-side} #basics-polygon
Minimal example demonstrating the most basic functionality of GDSFactory: creating a polygon on a specified layer. (a) Shows the code snippet in `python` including descriptive comments to highlight selected aspects. All code snippets used throughout this paper can be run interactively in the [online version of this paper](https://github.com/gdsfactory/photonics-paper). All shown examples are part of the [GDSFactory documentation](https://gdsfactory.github.io/gdsfactory/). (b) The resulting GDSII layout as it would appear in the inline Jupyter notebook viewer shipped with `gdsfactory`. 
:::

[](#fig-basics-polygon) shows a minimal example how to create a polygon from a list of points on a specified layer. The snippets also demonstrate some of the steps required to get going:
1. As with any `python` library, the first step is to import `gdsfactory`. For convenience we will alias it as `gf`. 
2. Before we can start designing, we need to activate a process development kit (PDK) that defines the layers and design rules for a specific fabrication process. Here we use the generic PDK included with GDSFactory. We will discuss [](#sec-pdks) in more detail below.
3. Next we create a blank `Component` instance that will hold our geometry. It can be understood as an empty GDS cell, that is enriched with additional functionality like metadata and ports.
4. Finally we add the desired polygon to the component by specifying the list of points and the GDS layer we want to add it to.
5. Lastly we visualize the created geometry using the built-in plotting functionality. In this case we use the inline viewer for Jupyter notebooks. However, GDSFactory also supports synchronization with KLayout for advanced visualization and verification. Leveraging the export capabilities of GDSFactory, the created layout can be saved and viewed as a GDSII or OASIS file ready for fabrication. (TODO correctly name available formats)

Defining more complex geometries from scratch can quickly become cumbersome. To alleviate this burden GDSFactory provides a rich library of predefined components ranging from geometrical primitives, over labels, structures for process controll like resolution tests and interlayer alignment calipers to common photonic building blocks like waveguides, bends, couplers, interferometers, ring resonators and more. These predefined parametric components can be easily reused in user-defined designed as is demonstrated in [](#fig-basics-predefined-components). Here we create a new blank component and add two realizations of predefined components: a text label and a rectangle. The parent component contains possibly multiple references to the underlying geometry, which can be manipulated individually.

:::{side-by-side} #basics-predefined-components
How to use predefined components. (a) Code snippet demonstrating how to realize predefined components from the GDSFactory library. Subsequently the created geometry can placed (possibly multiple times) into a parent component. The position and orientation of each reference can be manipulated individually. (b) Resulting layout showing the placed rectangle and two instances of the text label with different positions and orientation.
:::

### Functions as Parametric Cells (PCells)
As we have seen in [](#fig-basics-predefined-components) GDSFactory provides a mechanism to handle parametric components, that is components whose concrete geometry depends on a set of parameters. Such parametric components are commonly referred to as parametric cells (PCells). In GDSFactory PCells are defined as `python` functions decorated with `@gf.cell`. These functions take parameters as input and have to return a `gf.Component` instance containing the generated geometry. As such, the PCell definitions inherit the full power and flexibility of the `python` ecosystem, including control flow and complex arithmetics.

:::{side-by-side} #basics-mzi-pcell
How to define new parametric cells (PCells). (a) Code snippet showing how to define a new parametric cell from a component factory, i.e. from a factory that returns a `gf.Component` when called with desired parameters. The particular example is a Mach-Zehnder-Interferometer (MZI) with a bend attached to the output waveguide demonstrating the functionality of directional ports (b) Resulting layout showing the created MZI leading into a bend. The radius of the bend is {si}`15 </micro/meter>` as specified when calling the PCell function. The armlengths, bend-radii, waveguide widths etc. are not further specified here, but rather taken from the default settings of the underlying components.
:::

[](#fig-basics-mzi-pcell) demonstrates how a new PCell can be created. PCells can nest other PCells in order to build arbitrarily complex Components. In this case, we are composing previously defined PCells - a Mach-Zehnder-Interferometer (MZI) and an Euler-bend[^euler] - exposing the radius of the output bend as an input parameter. Based on this ability to compose PCells, GDSFactory enables large scale hierarchical layouts, where the composition of simpler building blocks allows the designer to reduce complexity by hiding implementation details behind layers of abstraction.

[^euler]: An Euler-bend is a bend whose curvature changes linearly along its length, minimizing losses due to mode mismatch.

### (Automatic) Routing
Integrated photonics relies at its core on waveguides to route light between different devices on chip. In contrast to low-speed electrical interconnects, waveguides require careful matching of the cross-sectional geometry at all interfaces to avoid unwanted reflections and losses. To facilitate connecting different components, GDSFactory leverages directional ports. Each port defines not only its position, but also its orientation and cross-section, enabling reliable mutual alignment when connecting different components. In [](#fig-basics-mzi-pcell) we have already seen an example using said mechanism: Connecting port `o1` of the bend to `o2` of the MZI ensures their correct relative placement, respecting the orientation of the optical ports. To allow access to the ports of the newly created component, we export the unconnected ports of the nested components. Using `c.draw_ports()` we can visualize the resulting ports, and using `c.pprint_ports()` we can print their properties in a human-readable format.

:::{side-by-side} #basics-pprint-ports
Retreiving port information in a human readable form (a) Code snippet reusing the component `c_mzi_with_bend` previously defined in [](#fig-basics-mzi-pcell-code) (b) A table containing the port names, positions, orientations and cross-sections of the component
:::

Manually routing complex circuits quickly becomes cumbersome. To alleviate this burden GDSFactory provides a routing API for (semi-)automatic waveguide routing. Given a declarative description of the desired connections it can create single and bundled waveguide routes, that avoid obstacles and collisions between the bundled waveguides. A minimal demonstration of automatically routing a single connection is shown in [](#fig-basics-route-single).

:::{side-by-side} #basics-route-single
Automatic manhattan routing for a single waveguide connection (a) Code snippet demonstrating how to route a waveguide between two ports (b) Resulting layout showing the created 1x2 multi mode interferometers (MMI) with an automatically routed waveguides the two.
:::

### `YAML` based Composition for Large Scale Layouts
While defining PCells in `python` is very powerfull, one commonly simply desires to combine pre-existing building block into circuits (as we have already done in [](#compositing) and [](#routing)). In these cases it can be beneficial to describe the desired circuit in a netlist-like format. For this purpose GDSFactory establishes a `YAML` based representation. The specification equivalent to [](#routing) is shown in [](#yaml). 

:::::: {figure}
::::: {figure}
:label: fig-yaml-code
::::{card}
```yaml
name: mask_compact

instances:
  rings:
    # `pack_doe` is a special function that creates a Design of Experiments array.
    component: pack_doe
    settings:
      
      # It will create ring resonators with these different radii and coupling lengths.
      doe: ring_single
      max_size : [1500, null]
      settings:
        radius: [20, 30, 40, 50, 60]
        length_x: [1, 2, 3, 4, 5, 6]

      # This tells the function to generate all possible combinations of the specified radius and length_x values.
      do_permutations: True
      function:

        # After each unique ring is created, the add_fiber_array function is applied to it, adding grating couplers for testing.
        function: add_fiber_array
        settings:
            fanout_length: 200

  mzis:
    component: pack_doe_grid
    settings:
      doe: mzi
      settings:
        delta_length: [10, 100]
      do_permutations: True
      spacing: [10, 10]
      function: add_fiber_array

placements:
  rings:
    xmin: 50

  mzis:
    xmin: rings,east
```
::::
:::::

:::: {figure}
:label: fig-yaml-output
:::{embed} #yaml-flow
:remove-output: false
:remove-input: true
:::
::::

Declaratively describing the desired circuit in `YAML` format. (a) `YAML` that is fed to `gf.read.from_yaml()` to create a circuit layout. The example creates a design of experiments (DoE) array of ring resonators with varying radii and coupling lengths, as well as a grid of Mach-Zehnder Interferometers (MZIs) with different path length differences. Each component is automatically equipped with fiber arrays for testing. (b) Resulting layout showing the created DoE array of ring resonators on the left and the MZI grid on the right.
::::::

## Continuous Integration: Regression Tests
Demonstrate GDS-diff:
Rev 1:
fundamental comp -> derived component 1

Rev 2:
fundamental comp -> derived component 1 & derived component 2

To introduce derived comp 2 the design engineer introduced changes to fundamental comp -> regression in derived comp 1

-> show GDSdiff.

TODO: Which other Tests to show?

## Simulation and Optimization: Layout as Single Source of Truth
The GDSFactory ecosystem supports multiple solvers to simulate the physical behavior of the created design. These cover several aspects, like the optical behavior of single components via finite difference time domain simulations, the collective behavior of multiple coupled components via scattering matrix (S-matrix) circuit simulators, the propagation of thermal transients, electronic properties and more. The single source of truth providing the device geometry, is a key benefit of GDSFactory linking these different simulators together.

### Component-Level Simulation
Show extraction of:
- S-parameters of strip to slot
- S-parameters of coupler
- Electrical? Would need help for that!

Reference to Layer stack ([](#sec-pdks))
Show of 3D view.

### Circuit-Level Simulation
Circuit -> CROW with SAX
Optimize CROW (with minimax obj-functions)

(sec-pdks)=
## Process Development Kits (PDKs)
Few words: what is a PDK
### Structure of a PDK in GDSFactory
  - Layer Definitions
  - Cross-sections; Layer Stack
  - Cell-library
  - Design Rules
-> Maybe subsection for each?

### Currently Available PDKs
List openly accessible PDKs and PDKs that are available upon request / under NDA.
Emphasize portability of high level designs across foundrys.


# Verification
TODO: @tvt173 I need help here :/ I do not know much about Verification inf gdsfactory...

Design Rules important part of PDK. Guarantee foundry can fabricate specified structures accurately.
## Design Rule Check (DRC)
Uses KLayout for DRC
List of design rules supported out of the box
- Feature size
- Inclusion
- Density
...

## Layout vs. Schematic (LVS)
What is actually happening here?
Do we check `unterminated ports`?


# Measurement and Validation
Once design has been sucessfully verified it can be send of to the foundry (transmitting the design files to the foundry is called tape-out (historical reference))

## Metadata
Demonstrate Fiber Metadata.
Wafer prober compatibility.

## Teststructures
Nonexhaustive List: Available photonic/metrology teststructures (also litho/alignment etc.). Introduce DOE cell.
Final: add teststructures to case study mask to complete the tutorial.


# Conclusion
The paper has highlighted the key features and functionalities of GDSFactory for hardware design. By leveraging the power of `python`, GDSFactory empowers designers with a familiar and flexible programming language widely used in machine learning, scientific computing, and engineering. This enables seamless integration with existing software ecosystems and promotes code reuse and collaboration.

The verification and validation capabilities of GDSFactory play a crucial role in ensuring the manufacturability and functionality of the designed chips. From functional verification to design for robustness and manufacturing, GDSFactory offers tools and methods to design chips, detect potential issues, and optimize performance.

Furthermore, GDSFactory provides an interactive schematic capture feature that enhances the design process and facilitates the alignment between design intent and the produced layout. With support for SPICE and `YAML`, designers have the flexibility to define and modify schematics in a user-friendly manner, either visually or programmatically.

The ability to define test sequences and measurement parameters within GDSFactory streamlines the post-fabrication testing process. By establishing a clear measurement and data analysis pipeline, designers can evaluate the fabricated components against the design specifications, allowing them to identify and systematically eliminate potential flaws. In conclusion, GDSFactory is a comprehensive and extensible design automation tool that empowers designers to efficiently develop integrated circuits and components. Its `python`-driven workflow, combined with its integration capabilities, verification tools, schematic capture feature, and test sequence definition, provides a powerful platform for turning chip designs into validated products. 

# Acknowledgements
We would like to acknowledge all other contributors to the GDSFactory project who at the time of writing are: Simon Bilodeau (Google), Niko Savola (Google, Aalto University), Marc de Cea Falco (Google), Helge Gehring (Google), Yannick Augenstein (FlexCompute), Ryan Camacho (BYU), Sequoia Ploeg (BYU), Prof. Lukas Chrostowski (UBC), Erman Timurdogan (Lumentum), Damien Bonneau (PsiQuantum), Alec Hammond (Meta), Thomas Dorch (HyperLight), Alex Sludds (Lightmatter), Igal Bayn (Quantum Transistors), Skandan Chandrasekar (UWaterloo), Tim Ansell, Ardavan Oskoii (Meta), Bradley Snyder (Superlight) and Amro Tork (Mabrains). Erman Timurdogan contributed the GDSFactory design, verification and validation cycles figure and Dario Quintero contributed the GDSFactory microservices architecture figure.

We would also like to acknowledge the foundational work of other open-source developers: Adam McCaughan (PHIDL), Juan Sanchez (DEVSIM),  Matthias Köfferlein (Klayout), Ardavan Oskooi, Alec Hammond, Stephen Johnson (MEEP), Jesse Lu (FDTDZ), Dan Fritchman (VLSIR), Dario Quintero (PIEL), Floris Laporte (SAX, MEOW). 

# Availability
The source code of GDSFactory is available publicly on [github](https://github.com/gdsfactory/gdsfactory) under MIT license. The demonstrations presented here can be run interactively in the [online version of this paper](https://github.com/gdsfactory/photonics-paper). Similarly an extensive [documentation](https://gdsfactory.github.io/gdsfactory/) including further examples and a full overview of the API is available.
