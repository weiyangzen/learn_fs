# sources/user-network-fs/rclone/backend/archive/archive_internal_test.go

Purpose: End-to-end tests for archive backend reading zip and squashfs archives, including full trees, subdirectories, single files, range reads, seek reads, sizes, modtimes, and root-above-archive listing.

Important APIs/types/functions: Helper `run` executes external commands. `checkTree` opens archive and source remotes, runs `operations.Check` and `CheckDownload`, then verifies `NewObject`, contents, `SeekOption`, `RangeOption`, modtime precision, size, and string identity for every source object. `testArchive` creates random test files with `rclone test makefiles`, builds an archive via callback, and runs several `checkTree` scenarios. `TestArchiveZip` uses external `zip`; `TestArchiveSquashfs` uses `mksquashfs`.

Control flow: Tests create local temp input trees, generate 1000 files, create archive output, open `:archive:<archivePath>` and compare against source. Subdirectory and single-file paths validate rooting inside archives; root listing validates archive file replacement as directory.

State and persistence: Uses temporary directories and external archive files. Rclone cache is used via `cache.Get`. No persistent repo state.

Dependencies and integration points: Depends on local backend, external `rclone`, `zip`, and `mksquashfs` executables, operations package, filters, fstest helpers, and testify.

Risks: External command availability controls skips/failures. Generating 1000 files can be slow. The tests do not cover write operations because archive contents are read-only.

Test signals: Strong behavioral signal for archive path mapping and concrete zip/squashfs read support.
