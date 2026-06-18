# sources/sync-backup/casync/doc/conf.py

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/doc/conf.py -->
## sources/sync-backup/casync/doc/conf.py

Purpose: `doc/conf.py` configures Sphinx documentation generation for casync. It is a minimal Python 3 Sphinx configuration focused on reStructuredText sources, HTML output, and manual page generation.

Important settings: `extensions = ['sphinx.ext.todo']` enables todo directives. `templates_path`, `source_suffix`, `master_doc`, `project`, `version`, `release`, `language`, `exclude_patterns`, `pygments_style`, and `todo_include_todos` define core Sphinx behavior. `html_theme = 'alabaster'` and `html_static_path = ['_static']` configure HTML output. `htmlhelp_basename` names HTML Help output. `man_pages` defines one manual page, `casync(1)`, generated from the `casync` source.

Control flow: Sphinx executes this file as Python during documentation builds. There are no functions or classes; the file sets module globals read by Sphinx.

State and persistence: it does not persist state itself. Sphinx uses it to generate build artifacts in the Meson build directory and installed man pages through `doc/meson.build`.

Dependencies and integration points: depends on Sphinx and the `sphinx.ext.todo` extension. It integrates with `doc/meson.build`, which invokes `sphinx-build` for man output when the Meson `man` option is enabled.

Risks: version and release are hardcoded to `1`, while the Meson project version is `2`, so generated docs may report stale version metadata. `language = None` is accepted by older Sphinx but can warn on newer versions. `_static` and `_templates` are referenced even if absent, which may warn depending on Sphinx configuration.

Test signals: Meson's `man` custom target is the primary validation. A successful `sphinx-build -b man` should produce `casync.1`; warnings about version drift or missing static paths would indicate maintenance issues.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/doc/conf.py -->
