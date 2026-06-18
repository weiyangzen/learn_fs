# File Research: sources/os/plan9/plan9/sys/src/cmd/cdfs/scsi.c

This file wraps Plan 9 raw SCSI device access for `cdfs`.

Key behavior:
- Loads optional sense-code text from `/sys/lib/scsicodes` and maps ASC/ASCQ pairs to readable errors.
- `_scsicmd()` writes CDBs to a raw device, transfers read/write/no-data payloads, then reads command status.
- `scsiready()` sends test-unit-ready with retries.
- `scsi()` serializes access with `QLock`, issues commands, requests sense on failure, retries limited media-change/not-ready cases, and updates media change state.
- `openscsi()` opens `<dev>/raw`, reads `<dev>/ctl` inquiry text, verifies readiness, and builds a `Scsi`.
- `closescsi()` frees the SCSI handle.

Important details:
- Read-TOC failures are common, so verbosity treats them specially.
- Recovered read errors are treated as successful data transfers.
- Write commands are not retried in the general retry loop.
- Media change updates `nchange` and `changetime`, which feed `cdfs` Qid versions.

Filesystem relevance:
- Direct. Provides raw device command transport and media-change detection for the `cdfs` filesystem.
