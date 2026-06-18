# sources/user-network-fs/pyfuse3/rst/conf.py

Purpose: Sphinx configuration for pyfuse3 documentation. It configures autodoc, intersphinx, nitpicky reference checking, project metadata, HTML output, and a workaround for Sphinx 9 native type-stub autodoc behavior.

Important APIs/types/functions: Sets `SPHINX_AUTODOC_IGNORE_NATIVE_MODULE_TYPE_STUBS=1`, enables `sphinx.ext.autodoc` and `sphinx.ext.intersphinx`, maps Python and Trio docs, sets `nitpicky=True`, derives `version`/`release` from `importlib.metadata.version('pyfuse3')`, and defines HTML theme/static behavior.

Control flow: Sphinx executes this file at doc-build startup. Environment setup occurs before extension loading. Version detection falls back to `dev` if the package is unavailable.

State and persistence: Persists documentation policy only. Build-time state is limited to environment variable initialization and module-level Sphinx settings.

Dependencies and integration points: Depends on Sphinx and a built/installable pyfuse3 package for accurate autodoc. Intersphinx links integrate with Python and Trio documentation. `make_release.py` builds docs with `sphinx-build -W`.

Risks: `nitpicky=True` makes unresolved references fatal in strict builds. Autodoc depends on the compiled extension being importable, so doc builds can fail on systems without a successful native build.

Test signals: Release automation invokes Sphinx with warnings as errors. There are no direct unit tests for this config.
