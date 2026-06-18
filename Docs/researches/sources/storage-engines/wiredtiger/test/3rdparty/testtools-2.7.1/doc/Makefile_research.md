# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/doc/Makefile

Purpose: Sphinx documentation build makefile for testtools.

Important APIs, types, and functions: variables include `SPHINXOPTS`, `SPHINXBUILD`, `PAPER`, `BUILDDIR`, and derived `ALLSPHINXOPTS`. Targets cover `help`, `clean`, `html`, `dirhtml`, `pickle`, `json`, `htmlhelp`, `qthelp`, `latex`, `changes`, `linkcheck`, and `doctest`.

Control flow: each target invokes `sphinx-build` with a selected builder and writes output under `_build/<builder>`. `clean` removes build outputs. Help targets print available commands.

State and persistence: generated docs are persisted under `doc/_build`; `clean` deletes that tree.

Dependencies and integration points: depends on Sphinx and `doc/conf.py`. Parent `Makefile` invokes this makefile for `clean-sphinx`, `html-sphinx`, and docs CI.

Risks and test signals: uses older Sphinx variable names such as `latex_paper_size`, and the output assumes Sphinx supports all listed builders. Test signals are successful `make html`, `make doctest`, and CI `make clean-sphinx docs`.
