---
title: GDSFactory - The open ecosystem for EPIC design.
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
    template: lapreprint
---

+++ { "part": "abstract" }

Designing an EPIC -- and (electronic) photonic integrated circuit -- requires robust tooling ranging from exploratory simulation via mask layout and verification to validation. In the past a variety of specialized syntaxes were introduced with similar tooling for electronic chip design -- the older cousin of EPICs. The relatively young age of integrated photonics opens up the opportunity to establish an accessible workflow which is intuitive, easily customizeable and extensible. GDSFactory is a Python based framework to build EPICs that provides a common syntax for design/layout, simulation (Ansys Lumerical, tidy3d, MEEP, MPB, DEVSIM, SAX, Elmer, Palace, …), verification (Klayout DRC, LVS, netlist extraction, connectivity checks, fabrication models) and validation. This paper showcases the capabilities of GDSFactory, highlighting its end-to-end workflow, which enables users to turn their chip designs into working products.
+++

# Introduction

Hardware iterations typically require months of time and involve substantial financial investments, often in the millions of dollars. In contrast, software iterations can be completed within hours and at a significantly lower cost, typically in the hundreds of dollars. Recognizing this discrepancy, GDSFactory aims to bridge the gap by leveraging the advantages of software workflows in the context of hardware chip development.

To achieve this, GDSFactory offers a comprehensive solution through a unified Python API. This API enables users to drive various aspects of the chip development process, including layout design, verification (such as optimization, simulation, and design rule checking), and validation (through the implementation of test protocols). By consolidating these functionalities into a single interface, GDSFactory streamlines the workflow and enhances the efficiency of hardware chip development.

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

```python
import gdsfactory as gf

@gf.cell
def mzi_with_bend(radius: float=10)->gf.Component:
    c = gf.Component()
    ...
```

You can also describe automated single or bundles or routes between different components. 

The python and YAML syntax are equivalent. You can also write a PCell as below.

## Schematic Driven Layout
For complex circuits you can start with a Schematic view that you can convert to YAML.


## Simulations directly from Layout
GDSFactory python API enables linking together different solvers so that you don’t have to draw the geometry twice. `I would actually emphasize, the reduced risk of mistakes, when all solvers etc. rely on the same geometry (ground truth)`. Solvers work both at the device, circuit and system level.

# Conclusion
The paper has highlighted the key features and functionalities of GDSFactory for hardware design. By leveraging the power of Python, GDSFactory empowers designers with a familiar and flexible programming language widely used in machine learning, scientific computing, and engineering. This enables seamless integration with existing software ecosystems and promotes code reuse and collaboration.

The verification and validation capabilities of GDSFactory play a crucial role in ensuring the manufacturability and functionality of the designed chips. From functional verification to design for robustness and manufacturing, GDSFactory offers tools and methods to design chips, detect potential issues, and optimize performance.

Furthermore, GDSFactory provides an interactive schematic capture feature that enhances the design process and facilitates the alignment between design intent and the produced layout. With support for SPICE and YAML, designers have the flexibility to define and modify schematics in a user-friendly manner, either visually or programmatically.

The ability to define test sequences and measurement parameters within GDSFactory streamlines the post-fabrication testing process. By establishing a clear measurement and data analysis pipeline, designers can evaluate the fabricated components against the design specifications, ensuring the delivery of known good dies. In conclusion, GDSFactory is a comprehensive and extensible design automation tool that empowers designers to efficiently develop integrated circuits and components. Its Python-driven workflow, combined with its integration capabilities, verification tools, schematic capture feature, and test sequence definition, provides a powerful platform for turning chip designs into validated products. 

# Acknowledgements
We would like to acknowledge all of the contributors to the GDSFactory project who at the time of writing are: Joaquin Matres Abril (DoPlayDo), Simon Bilodeau (Google), Niko Savola (Google, Aalto University), Marc de Cea Falco (Google), Helge Gehring (Google), Yannick Augenstein (FlexCompute), Troy Tamas (GDSFactory), Ryan Camacho (BYU), Sequoia Ploeg (BYU), Prof. Lukas Chrostowski (UBC), Erman Timurdogan (Lumentum),  Sebastian Goeldi (PsiQuantum), Damien Bonneau (PsiQuantum), Floris Laporte (GDSFactory), Alec Hammond (Meta), Thomas Dorch (HyperLight), Jan David Fischbach (KIT), Alex Sludds (Lightmatter), Igal Bayn (Quantum Transistors), Skandan Chandrasekar (UWaterloo), Tim Ansell, Ardavan Oskoii (Meta), Bradley Snyder (Superlight) and Amro Tork (Mabrains). Some of the GDSFactory authors have also contributed to other pictures in the paper, Erman Timurdogan contributed the GDSFactory design, verification and validation cycles figure and Dario Quintero contributed the GDSFactory microservices architecture figure.

We would also like to acknowledge the foundational work of other open-source developers: Adam McCaughan (PHIDL), Juan Sanchez (DEVSIM),  Matthias Köfferlein (Klayout), Ardavan Oskooi, Alec Hammond, Stephen Johnson (MEEP), Jesse Lu (FDTDZ), Dan Fritchman (VLSIR), Dario Quintero (PIEL), Floris Laporte (SAX, MEOW). 
