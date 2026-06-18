# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/doc/conf.py

Purpose: Sphinx configuration for building testtools documentation.

Important APIs, types, and functions: enables `sphinx.ext.autodoc` and `sphinx.ext.intersphinx`; sets `templates_path`, `source_suffix`, `master_doc`, `project`, copyright, `version`, `release`, `pygments_style`, `html_theme`, `html_static_path`, `htmlhelp_basename`, `latex_documents`, and `intersphinx_mapping` for Python 2, Python 3, and Twisted docs.

Control flow: Sphinx imports this file, reads global configuration values, then uses them for HTML, LaTeX, help, doctest, linkcheck, and intersphinx builders.

State and persistence: no application runtime state. Sphinx writes persistent build output under `_build` as directed by `doc/Makefile`.

Dependencies and integration points: depends on Sphinx and remote intersphinx inventories. Integrates with package documentation sources and CI docs build.

Risks and test signals: `version` and `release` are literal placeholders unless release tooling rewrites them. `exclude_trees` is legacy relative to newer Sphinx `exclude_patterns`. Test signals are clean Sphinx builds and working intersphinx references.
