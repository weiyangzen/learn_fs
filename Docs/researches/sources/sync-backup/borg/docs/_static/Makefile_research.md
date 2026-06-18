# sources/sync-backup/borg/docs/_static/Makefile Research

## Purpose

`docs/_static/Makefile` builds static logo assets from `logo.svg` for documentation outputs. It creates `logo.pdf` for LaTeX/PDF builds and `logo.png` for raster uses.

## Important APIs, Types, and Functions

The `all` target depends on `logo.pdf` and `logo.png`. `logo.pdf` runs `inkscape logo.svg --export-pdf=logo.pdf`; `logo.png` runs `inkscape logo.svg --export-png=logo.png --export-dpi=72,72`; `clean` removes generated logo files.

## Control Flow

Make rebuilds the generated assets when `logo.svg` is newer or outputs are absent. `clean` deletes both outputs.

## State and Persistence Behavior

The file writes `logo.pdf` and `logo.png` in `docs/_static` and removes them on clean. It does not alter `logo.svg`.

## Dependencies and Integration Points

It depends on Inkscape CLI compatibility. `docs/conf.py` references `_static/logo.svg` for HTML and `_static/logo.pdf` for LaTeX, so the PDF output is relevant to documentation PDF builds.

## Risks and Edge Cases

Inkscape CLI flags have changed across versions; newer Inkscape versions may prefer different export option syntax. If `logo.pdf` is not prebuilt and Inkscape is unavailable in the docs environment, LaTeX builds can fail.

## Test Signals

Run `make -C docs/_static all` with the expected Inkscape version and verify both output files. PDF documentation builds validate the `logo.pdf` path.
