# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_p2l_upgrade.c

Defines P2L checkpoint metadata upgrade from v1 to v2.

Behavior:
- Requires major-upgrade eligibility and pre-creates/opens a v2 P2L checkpoint region sized by `layout.p2l.ckpt_pages`.
- Creates heap metadata object for the new region.
- Clears the region with default metadata/VSS and completes upgrade.

Notable TODO:
- Mentions validation for no open bands is still needed.
