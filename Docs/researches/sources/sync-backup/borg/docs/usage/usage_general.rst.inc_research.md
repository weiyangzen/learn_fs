# sources/sync-backup/borg/docs/usage/usage_general.rst.inc

Purpose: Aggregates general usage documentation includes for the `docs/usage/` section.

Important APIs/types/functions: This file has no CLI command surface. It is a Sphinx composition file including general topics: positional arguments, repository URLs/locations, archive specification, logging, return codes, config, environment variables, file systems, units, date/time, resources, and file metadata. It defines anchors `_config`, `_env_vars`, and `_platforms`.

Control flow: Sphinx resolves the includes in order when building usage documentation. Anchors placed before selected includes provide cross-reference targets.

State and persistence: No runtime state or persistence; it only affects generated documentation structure and cross-reference resolution.

Dependencies and integration points: Depends on the existence and relative paths of `docs/usage/general/*.rst.inc`. Integrated command pages link to these common topics and `common_options`.

Risks: Missing or moved include files break docs builds. Anchor drift can break external and internal links.

Test signals: `tox -e docs` or `python scripts/make.py build_usage` followed by Sphinx build with nitpicky/warnings-as-errors should catch missing includes and references.
