## sources/user-network-fs/gcsfuse/internal/util/diskutil/disk_util.go

Purpose: Disk allocation helpers for estimating on-disk file size and discovering filesystem block size.

Important APIs/types/functions: constants `defaultVolumeBlockSize` and `maxVolumeBlockSize`; `GetSpeculativeFileSizeOnDisk(fileContentSize, volumeBlockSize)`; `GetVolumeBlockSize(path)`.

Control flow: speculative size rounds content bytes up to block size unless block size is 0 or 1. Volume block size calls `syscall.Statfs`, prefers `Frsize` over `Bsize`, and falls back to 4096 on statfs errors, zero, or suspiciously large block sizes.

State and persistence behavior: no persistence; reads filesystem metadata and logs fallback decisions.

Dependencies and integration points: used by cache/disk-accounting code that needs conservative allocation estimates.

Risks: syscall is Unix-specific. Overflow is not explicitly guarded in rounding formula for extreme sizes. Fallback log messages reference `Bsize` even when `Frsize` was used.

Test signals: `disk_util_test.go` covers rounding cases, valid temp directory block size, and invalid path fallback.
