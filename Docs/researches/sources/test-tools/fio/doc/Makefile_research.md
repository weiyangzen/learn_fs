# sources/test-tools/fio/doc/Makefile

Purpose: Sphinx documentation build Makefile for fio, providing common output formats.

Important APIs/targets: Variables include `SPHINXOPTS=-W --keep-going`, `SPHINXBUILD`, `PAPER`, `BUILDDIR`, `ALLSPHINXOPTS`, and `I18NSPHINXOPTS`. Targets include `html`, `dirhtml`, `singlehtml`, `pickle`, `json`, `htmlhelp`, `qthelp`, `applehelp`, `devhelp`, `epub`, `epub3`, `latex`, `latexpdf`, `latexpdfja`, `text`, `man`, `texinfo`, `info`, `gettext`, `changes`, `linkcheck`, `doctest`, `coverage`, `xml`, `pseudoxml`, `dummy`, and `clean`.

Control flow: Each target invokes `sphinx-build` with the selected builder, shared doctree output under `output/doctrees`, and builder-specific output directories. PDF/info targets run secondary make commands inside generated trees.

State/persistence: Generated documentation lives under `doc/output`; `clean` removes its contents.

Dependencies/integration: Depends on Sphinx, optional LaTeX/tooling for PDF, qthelp/devhelp/applehelp tools for platform-specific formats, and `conf.py`.

Risks: `-W` treats warnings as errors, so documentation warnings break builds. `make -C` for `info` uses bare `make` instead of `$(MAKE)`. The help target lists many builders, but environment support may vary.

Test signals: `make dummy` provides a syntax-only signal; CI usually uses `html` or `man` to catch warning regressions.
