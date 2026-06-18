# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_trim_upgrade.c

Defines trim log metadata upgrade from v0 to v1.

Behavior:
- Requires major-upgrade eligibility and pre-creates/opens a v1 trim log region with one `struct ftl_trim_log` entry.
- Creates heap metadata for the v1 region.
- Clears the metadata region, then completes the layout upgrade.

Risk:
- Contains a misleading comment saying “NV cache metadata region - v2”; the actual code upgrades trim log to `FTL_TRIM_LOG_VERSION_1`.
