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

## Note on side-by-side view
We use an experimental side-by-side plugin for myst to display code and its results side by side. This requires a special version of mystmd
https://github.com/jan-david-fischbach/mystmd/commit/1c48b77e5ec6c8982b9f0f6f6135991dffcb5619 to avoid typst syntax errors.
