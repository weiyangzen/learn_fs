# sources/sync-backup/restic/doc/Makefile

## Purpose

This Makefile is a minimal Sphinx documentation build wrapper. It exposes the standard Sphinx "make mode" targets and an `autobuild` helper for live HTML documentation development.

## Important APIs, Types, and Functions

- Variables: `SPHINXOPTS`, `SPHINXBUILD`, `SPHINXPROJ`, `SOURCEDIR`, and `BUILDDIR`.
- `help` target runs `sphinx-build -M help`.
- Pattern target `%: Makefile` forwards arbitrary make targets to `sphinx-build -M <target>`.
- `autobuild` runs `sphinx-autobuild -b html -i '.doctrees/*' . _build`.

## Control Flow

`make` defaults to `help` because the `help` target appears first. Any unknown target, such as `html`, `dirhtml`, or `linkcheck`, is routed to Sphinx's make-mode builder with source directory `.` and build directory `_build`. `O` can pass extra options to Sphinx as a shortcut for `SPHINXOPTS`.

## State and Persistence Behavior

Build outputs are written below `_build`. `autobuild` watches the documentation tree and refreshes generated HTML while ignoring `.doctrees` output. The Makefile itself does not delete outputs.

## Dependencies and Integration Points

It depends on `sphinx-build` and optionally `sphinx-autobuild`. It is configured by `doc/conf.py` and the `.rst` documentation tree in the same directory. It integrates with local developer workflows and CI/documentation builds that call `make -C doc html` or similar.

## Risks and Edge Cases

- Missing Sphinx or theme dependencies cause targets to fail.
- The catch-all target will forward typos to Sphinx, so user feedback depends on Sphinx's target handling.
- `autobuild` assumes `sphinx-autobuild` is installed locally.

## Test Signals

Successful `make html` or `make linkcheck` in `doc/` validates the Makefile, Sphinx config, and documentation source compatibility.
