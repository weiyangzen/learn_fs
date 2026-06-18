# sources/sync-backup/borg/docs/usage_general.rst.inc

Purpose: Legacy/top-level aggregate include for general Borg usage topics outside the nested `docs/usage/` directory.

Important APIs/types/functions: It contains only Sphinx include directives for `usage/general/*` topics: positional arguments, repository URLs/locations, logging, return codes, environment, file systems, units, date/time, resources, and file metadata.

Control flow: Sphinx expands these includes in order wherever this file is included. Unlike `docs/usage/usage_general.rst.inc`, this variant does not include archive specification/config anchors.

State and persistence: No runtime state; documentation composition only.

Dependencies and integration points: Depends on relative include layout under `docs/usage/general/`. It likely supports older or broader docs pages that include `docs/usage_general.rst.inc`.

Risks: Divergence between this and `docs/usage/usage_general.rst.inc` can lead to inconsistent common docs coverage. Missing includes break docs builds.

Test signals: Sphinx docs build catches missing includes and unresolved references; review should compare common topic coverage between the two aggregate files.
