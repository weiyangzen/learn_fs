# sources/sync-backup/borg/docs/conf.py Research

## Purpose

`docs/conf.py` is BorgBackup's Sphinx configuration. It sets project metadata, derives documentation version from `borg.__version__`, configures HTML/theme/static behavior, LaTeX/man-page output, extensions, and small Sphinx runtime hooks.

## Important APIs, Types, and Functions

The config inserts `../src` into `sys.path` and imports `borg.__version__ as sw_version`. It computes `version` by splitting at `+` or `-`, sets `release = version`, defines `project`, copyright, source suffix, master doc, warning suppression, `primary_domain = "rst"`, and Pygments style. It imports `guzzle_sphinx_theme`, sets `html_theme_path`, `html_theme`, `html_theme_options`, logo/favicon/static/extra paths, sidebar templates, index/source-link/footer options, and LaTeX settings. `set_rst_settings(app)` updates docutils settings to remove field/option name limits, and `setup(app)` loads `sphinxcontrib.jquery`, adds `css/borg.css`, and connects the hook. `extensions` is finally set to include extlinks, autodoc, todo, coverage, viewcode, jquery, and guzzle theme. `extlinks` defines GitHub issue links.

## Control Flow

Sphinx imports this file during build. Import-time code adjusts `sys.path`, imports Borg and theme modules, computes config values, and registers the `setup()` hook. On builder initialization, the hook mutates `app.env.settings`.

## State and Persistence Behavior

The file does not persist state itself, but it controls generated HTML, LaTeX, man-page, and help output. Importing Borg during docs build can execute package import side effects and requires dependencies needed for the import to succeed.

## Dependencies and Integration Points

It integrates with Borg package metadata, Sphinx, docutils, `guzzle_sphinx_theme`, `sphinxcontrib.jquery`, static assets under docs, `src/borg/paperkey.html`, Read the Docs config, and docs Makefile builders. LaTeX output depends on `_static/logo.pdf` and selected appendices.

## Risks and Edge Cases

Importing `borg` to get the version couples docs builds to package importability. There are two assignments to `extensions`; the initial empty list is replaced later, which is harmless but can confuse maintenance. Theme dependencies must be installed in docs environments. Version splitting assumes local versions contain `+` or prerelease/build separators use `-`; unusual version strings may produce unexpected display versions.

## Test Signals

Run Sphinx HTML, man, and LaTeX/PDF builds with the same requirements as Read the Docs. Confirm version rendering, sidebar/theme assets, issue extlinks, and `paperkey.html` inclusion.
