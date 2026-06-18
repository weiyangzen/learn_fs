# File Research: sources/local-fs/xfsprogs/repair/agheader.c

## Purpose
Verifies and repairs allocation group headers: AG superblocks, AGF, and AGI.

## Key Elements
`verify_set_agf` checks AGF magic, version, sequence number, length, freelist indexes, and v5 UUID, repairing fields unless `no_modify` is set. `verify_set_agi` does analogous checks for AGI magic, version, sequence, length, and UUID.

`compare_sb` compares geometry from a candidate superblock to the mounted primary superblock, ignoring transient/counter fields. `check_v5_feature_mismatch` synchronizes secondary v5 feature fields with the primary, with special handling for `NEEDSREPAIR` and log-incompat feature semantics.

`secondary_sb_whack` determines the valid on-disk superblock field extent for the feature set, zeros garbage beyond it, clears invalid flags, handles quota or metadir-era inode fields, normalizes alignment/stripe/sector fields when feature bits do not justify them, and clears secondary `needsrepair`.

`verify_set_agheader` runs superblock verification/comparison, resets a bad superblock from the primary geometry when repair is allowed, sanitizes secondary-super fields, then verifies AGF and AGI.

## Dependencies
Depends on libxfs superblock/AG structures and feature helpers, repair globals such as `no_modify` and `features_changed`, warning/error helpers, and `agheader.h` geometry structures.

## Behavior/Risks
The code is intentionally conservative around primary-vs-secondary differences because older mkfs and growfs behavior can leave valid historical variations. Return bits identify which AG structures were changed so callers can decide what to write and report.
