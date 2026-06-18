# sources/sync-backup/borg/docs/Makefile Research

## Purpose

`docs/Makefile` is BorgBackup's Sphinx documentation build wrapper. It exposes common Sphinx builders such as HTML, dirhtml, singlehtml, epub, LaTeX, PDF, text, man pages, linkcheck, doctest, and changes.

## Important APIs, Types, and Functions

Configurable variables are `SPHINXOPTS`, `SPHINXBUILD`, `PAPER`, and `BUILDDIR`. `ALLSPHINXOPTS` passes doctree output, paper settings, extra options, and the current docs directory to Sphinx. Targets invoke `$(SPHINXBUILD) -b <builder> $(ALLSPHINXOPTS) $(BUILDDIR)/<builder>`, with `latexpdf` running `make -C $(BUILDDIR)/latex all-pdf`.

## Control Flow

Users run a make target; the target invokes Sphinx and prints a completion hint. `clean` removes build output. The `help` target lists available builders. The `.PHONY` declaration names documentation targets.

## State and Persistence Behavior

The Makefile writes generated documentation under `docs/_build` by default and removes it on `clean`. It does not modify source docs.

## Dependencies and Integration Points

It integrates with Sphinx, `docs/conf.py`, docs source `.rst` files, LaTeX toolchains for PDF, linkcheck network behavior, and doctest-enabled documentation. CI/readthedocs may call equivalent Sphinx builders rather than this Makefile directly.

## Risks and Edge Cases

The Makefile assumes `sphinx-build` is on PATH unless overridden. `latexpdf` assumes the generated LaTeX directory has a working Makefile and TeX toolchain. Network-sensitive `linkcheck` can be flaky. The target set is broad but conventional; failures usually reflect dependencies or Sphinx config.

## Test Signals

Run `make -C docs html`, `make -C docs man`, and `make -C docs linkcheck` as appropriate. Read the Docs builds and tox docs environments are external validation signals.
