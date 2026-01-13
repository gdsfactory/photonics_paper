# Work in Progress: Paper introducing GDSfactory to the scientific community

We will target the integrated photonics community first, as it is the core expertise of GDSFactory. Later we might add further contributions also reach the Analog/MEMS people.

To start the web version of the paper, run:

```bash
uv run myst start --execute
```

To build the PDF version of the paper, run:

```bash
uv run myst build --pdf --execute
```

Should you run into problems with warnings about klive interfering with the typst build, you can suppress those warnings by:

```bash
rm -rf ./_build/execute
KFACTORY_LOGFILTER_LEVEL="ERROR" myst build --pdf --execute
```