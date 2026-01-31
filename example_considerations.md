Instead of having a dedicated section with a case study, I would like to use examples from a case study throughout the paper. For that, I need a PIC case study that allows me to demonstrate the following features of gdsfactory:
1. Define primitive polygon geometry
2. Reusing predefined components
3. Defining custom PCells as python functions returning components (component factory)
4. Ports (optical and electrical)
5. (automatic) Routing
6. YAML based flow
  - Pack/Grid
7. Regression tests 
  - Rev 1: fundamental comp -> derived component 1
  - Rev 2: fundamental comp -> derived component 1 & derived component 2
  - To introduce derived comp 2 the design engineer introduced changes to fundamental comp -> regression in derived comp 1 -> show GDSdiff.
8. Component level Simulation & Optimization (i.e. inverse design) (e.g. grating coupler and directional coupler for ring resonators)
9. Circuit level Simulation & Optimization (Via SAX; A CROW filter would probably be a nice example)
10. Electrical/Thermal simulation (gsim)
  - Tuners
  - Modulators (travelling wave)
11. Process development kits 
  - Layer Definitions
  - Cross-sections; Layer Stack
  - Cell-library
  - Design Rules
12. Verification
  - Design Rule Check (dummy fill)
  - Layout vs. Schematic
13. Measurement and Validation
  - Metadata: Location of Fibercouplers; Measurement Schema; Wafer prober compatibility
  - Teststructures: Processcontrol; Litho/Alignment; DOE; Cutback; TLM
  
I think it might make sense to use a simple C-band transceiver chip with 4 fibers and 8 WDM channels per fiber. The coarse division of the input light into two bands is done by a CROW. Each of the bands is then split into 4 channels using OADMs. Strip to slot converters -> Slot Polymer Modulators -> slot to strip -> Merge using OADMs and second CROW -> Out. On the receiving side: Fiber -> CROW/OADM demux -> Germanium PDs. Additional teststructures are placed around the design. 
