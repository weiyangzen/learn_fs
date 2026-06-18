# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_layout_upgrade.h

Public interface for FTL metadata layout upgrades.

Defines:
- Upgrade result enum.
- Verify and upgrade callback types.
- Per-version `ftl_region_upgrade_desc`.
- Per-region descriptor list.
- `ftl_layout_upgrade_ctx`.
- APIs for checking upgrade eligibility, superblock upgrade, layout verification, region upgrade, completion, next-region selection, and latest-version query.

Contract:
- Region upgrade functions are usually asynchronous and must call `ftl_region_upgrade_completed()` when persisted conversion finishes.
