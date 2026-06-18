# sources/test-tools/lcov/docs/conf.py Research

Purpose: this is the Sphinx configuration and lightweight extension for LCOV documentation. It sets project metadata, theme behavior, man-page discovery, dynamic index generation, substitutions, and intersphinx mapping.

Important APIs and functions: module-level `ToolName`, `TOOLNAME`, `release`, `version`, `build_date`, `extensions`, HTML settings, and `manpages_url` define global Sphinx config. `get_man_pages()` scans `docs/man/*.rst` and returns Sphinx `man_pages` tuples. `generate_index_rst(app, docname, source)` replaces the `index` document at read time with generated RST. `setup(app)` connects the `source-read` event.

Control flow: import-time code reads environment overrides, computes metadata, discovers man pages, and sets config variables. During Sphinx reading, `generate_index_rst` only handles `docname == "index"`, lists all man page stems, inserts a generated overview, callback-script descriptions, getting-started text, included example README, authors, and license text.

State and persistence: no durable state is written by this file. It reads RST files from `docs/man` and `../example/README.rst` is referenced through an include in generated content.

Dependencies and integration: depends on Sphinx, `sphinx_rtd_theme`, pathlib, regex, environment variables from the Makefile, and the LCOV docs tree. It integrates generated manual pages into both HTML and man builders.

Risks: the generated RST contains minor markup issues such as stray backticks in criteria/unreachable entries and wording typos. `read_text()` uses default encoding. Dynamic index generation means missing `man` files or missing `../example/README.rst` can fail at build time. `intersphinx_mapping` is defined twice.

Test signals: build HTML/man outputs with default and custom `TOOL_NAME`, verify man page section/description extraction from multiple title styles, run with no man pages, inspect generated index warnings, and confirm substitutions render in RST pages.
