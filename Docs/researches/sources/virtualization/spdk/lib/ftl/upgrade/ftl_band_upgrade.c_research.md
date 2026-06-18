# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_band_upgrade.c

Defines band metadata region upgrade from v1 to v2.

Behavior:
- Verification requires clean upgrade eligibility and pre-creates/opens the v2 region.
- Upgrade reads old metadata, shifts each `struct ftl_band_md` contents by the new `version` field size, sets `FTL_BAND_VERSION_2`, and requires bands to be only `CLOSED` or `FREE`.
- Persists converted metadata to the v2 region, then calls `ftl_region_upgrade_completed()`.

Risk:
- This is layout-sensitive binary structure conversion; the static assert requires `struct ftl_band_md` to remain exactly one FTL block.
