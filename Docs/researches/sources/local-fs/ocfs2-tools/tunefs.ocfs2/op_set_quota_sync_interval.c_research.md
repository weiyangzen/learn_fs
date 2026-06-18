# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_quota_sync_interval.c

## Role

Implements `--usrquota-sync-interval <ms>` and `--grpquota-sync-interval <ms>`, changing the interval used to sync local quota structures to global quota files.

## Parse Flow

`set_quota_sync_interval_parse_option()` parses an unsigned decimal integer with `strtoul()`. It requires:

- fully numeric input
- minimum `100`
- maximum `4294967295`
- not `ULONG_MAX`

The value is stored directly in `op->to_private` via integer-to-pointer cast.

## Run Flow

`update_sync_interval()` checks that the relevant quota feature is enabled, initializes quota info, reads global quota info, compares the existing `dqi_syncms`, prompts if changing, writes the new interval to `fs->qinfo[type].qi_info.dqi_syncms`, and calls `ocfs2_write_global_quota_info()` under signal blocking.

## Metadata Touched

- Global user or group quota info file, specifically `dqi_syncms`

## Open Flags

Both operations are declared `TUNEFS_FLAG_RW`.

## Notable Risks

- The integer value is carried through `void *`. This is common in older C code but not type-safe and relies on pointer width being sufficient.
- On progress allocation failure, the code calls `tcom_err(err, ...)` where `err` may contain the previous successful value rather than `TUNEFS_ET_NO_MEMORY`.
