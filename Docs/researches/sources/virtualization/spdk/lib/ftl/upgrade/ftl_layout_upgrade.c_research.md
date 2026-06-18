# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_layout_upgrade.c

Core metadata-layout upgrade engine.

Important behavior:
- Defines descriptor table mapping region types to latest versions and per-version upgrade descriptors.
- `ftl_region_upgrade_enabled()` only allows upgrades after clean shutdown and not SHM-clean state.
- `ftl_region_major_upgrade_enabled()` additionally requires `dev->sb->upgrade_ready`.
- `ftl_layout_verify()` validates regions and runs verify callbacks for every outdated region.
- `ftl_region_upgrade()` dispatches one version upgrade.
- `ftl_region_upgrade_completed()` updates superblock layout tracking, entry sizing, and region version, then invokes callback.
- `ftl_superblock_upgrade()` synchronously upgrades SB versions before normal layout work.
- `ftl_layout_upgrade_init_ctx()` walks regions to select the next outdated region.
- `ftl_layout_upgrade_drop_region()` removes deprecated regions from bdev layout tracker.

Risk:
- Some descriptor entries are intentionally empty for non-upgradable/static regions; callers rely on `latest_ver` and `desc` being valid only where upgrades exist.
