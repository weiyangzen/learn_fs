# sources/sync-backup/restic/doc/conf.py

## Purpose

This is the Sphinx configuration for restic's documentation. It sets project metadata, extensions, source conventions, theme settings, GitHub integration metadata, static assets, exclusions, and external issue links.

## Important APIs, Types, and Functions

- `extensions` enables `sphinx.ext.extlinks` and `sphinx_rtd_theme`.
- `templates_path`, `source_suffix`, and `master_doc` configure source layout.
- `project`, `copyright`, and `author` provide metadata.
- `version` is read from `../VERSION`; `release` mirrors it.
- `exclude_patterns` skips build/system files and several documents included via `100_references.rst` to avoid duplicate labels.
- `html_theme`, `html_css_files`, `html_logo`, `html_favicon`, `html_show_version`, and `html_static_path` control HTML rendering.
- `html_context` enables GitHub edit/source links for the `restic/restic` repository and `master/doc/`.
- `extlinks` defines `:issue:` links to GitHub issues.

## Control Flow

Sphinx imports this file during builds. The only dynamic action is reading the first line of `../VERSION` to set `version` and `release`. Everything else is declarative module-level configuration.

## State and Persistence Behavior

The config reads the repository `VERSION` file. It does not write state. Generated documentation output is controlled by Sphinx and the Makefile, typically under `doc/_build`.

## Dependencies and Integration Points

It depends on Sphinx, `sphinx_rtd_theme`, static files in `_static`, custom CSS at `css/restic.css`, logo assets, and the documentation `.rst` tree. It integrates with Read the Docs-style theming and GitHub issue references.

## Risks and Edge Cases

- Opening `../VERSION` depends on Sphinx's working directory/import context being `doc/`, which is the normal Sphinx behavior.
- The copyright year is static and can drift.
- Excluded documents are still included indirectly; changing documentation references can reintroduce duplicate labels or hide pages unexpectedly.
- Theme/static asset paths must remain valid.

## Test Signals

Successful Sphinx builds through `doc/Makefile` validate this file. Link/reference checks can catch broken `extlinks`, duplicate labels, and missing excluded-document references.
