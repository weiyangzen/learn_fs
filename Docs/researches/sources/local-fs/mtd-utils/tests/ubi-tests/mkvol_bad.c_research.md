# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/mkvol_bad.c

## Role
Negative tests for UBI volume creation/removal ioctl validation.

## Main Behavior
- Confirms invalid volume IDs, alignments, sizes, volume types, and overlong names fail with expected errno values.
- Tests duplicate volume ID and duplicate volume name rejection.
- Tests failure when no free space remains.
- Creates up to the maximum volume count and tolerates `ENFILE` due to gluebi/MTD restrictions.
- Tests invalid removal IDs, removal of non-existing volumes, and double removal.

## Interfaces And Dependencies
- Uses `ubi_mkvol`, `ubi_rmvol`, `ubi_get_dev_info`.
- Uses helper `check_failed` to assert both failure and expected `errno`.

## Notes
- Cleanup loops attempt removal across possible volume IDs regardless of whether all were created.
- The “maximum size then create more” check expects `EEXIST` because it reuses the same name, even though the message describes space exhaustion.
