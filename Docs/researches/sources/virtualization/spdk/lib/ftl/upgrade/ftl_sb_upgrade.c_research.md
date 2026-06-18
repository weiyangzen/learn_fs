# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_upgrade.c

Defines superblock upgrade descriptors, currently v4 to v5.

Behavior:
- `sb_v4_to_v5_verify()` requires normal region-upgrade eligibility and rejects upgrade if any pending major region upgrade exists.
- Converts v3-style linked metadata layout records into NVC/base layout trackers, excluding fixed/free/deprecated categories.
- `sb_v4_to_v5_upgrade()` validates non-empty old blob area, loads old metadata layout, bumps header to v5, resets v5 blob descriptors, and leaves v5 layout blob empty for later storage.
- Older SB versions v0-v3 are disabled.

Risk:
- The verifier comparison appears suspicious: it treats `reg->current.version <= latest` as “only latest region version found,” but usually older versions are `< latest`; this may need cross-checking with surrounding layout semantics.
