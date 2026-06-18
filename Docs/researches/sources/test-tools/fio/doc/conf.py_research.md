# sources/test-tools/fio/doc/conf.py

Purpose: Sphinx configuration for fio documentation.

Important APIs/functions: Sets project metadata, source suffix, master document, templates, excluded patterns, pygments style, HTML theme, help output base names, LaTeX/man/Texinfo document definitions, and `todo_include_todos`. `fio_version()` reads or generates `FIO-VERSION-FILE` by invoking `FIO-VERSION-GEN`, then derives `version` and `release`.

Control flow: During Sphinx startup, Python imports this file, computes version/release, and applies builder settings. If the version file is missing, it calls the generator script in the workspace root and falls back to `Unknown` on failure.

State/persistence: May create/update `FIO-VERSION-FILE` through the generator. Generated docs go to Makefile output paths, not controlled here.

Dependencies/integration: Requires Sphinx, Python `os.path` and `subprocess`, the fio version generator, and `.rst` docs rooted at `index`/`fio_doc`.

Risks: `fio_version()` assumes the version file splits on `-` with at least two fields; malformed content can raise `IndexError`. Shell execution of `FIO-VERSION-GEN` depends on executable bit and shell environment. `master_doc='index'` while man pages point at `fio_doc`, so both source docs must exist.

Test signals: Run `sphinx-build -b dummy` or `make dummy`, plus a missing-version-file scenario to verify generation.
