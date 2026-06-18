# sources/user-network-fs/rclone/cmd/bisync/compare.go

Purpose: Computes the effective comparison policy for bisync listings, deltas, equality checks, and sync calls. It decides whether size, modtime, checksum, slow hashes, and download-hash are used.

Important APIs/types/functions: `CompareOpt` stores comparison booleans and selected hash types. `setCompareDefaults` derives defaults from global config and bisync flags. `sizeDiffers`, `hashDiffers`, and `timeDiffers` implement conservative difference predicates. `setHashType` chooses common or same-side hash types and handles slow hash settings. `setFromCompareFlag` parses `--compare`. `downloadHashOpt` and `tryDownloadHash` support MD5 computation by downloading objects.

Control flow: Defaults start as size+modtime. Global `--size-only`, `--checksum`, `--ignore-size`, and bisync `--compare` mutate that baseline. Slow-hash detection and no-slow/slow-sync-only flags may suppress listing hashes, keep checksums only for sync, or fall back to size/modtime. If no comparison method remains, setup fails. Unsupported global sync flags such as `--update`, `--no-check-dest`, and `--no-traverse` are logged and disabled.

State and persistence behavior: This file stores no files, but it mutates `Options.Compare`, `Options.IgnoreListingChecksum`, `downloadHashOpt`, and `fs.ConfigInfo` in the active context. `tryDownloadHash` registers accounting checking transfers and emits a first-use "Downloading hashes" notice once.

Dependencies and integration points: Used by `Bisync` before all run setup, by listing and delta comparison, by queue logger hash capture, by conflict resolution, and by recheck/equality code. It depends on rclone fs features (`SlowHash`, precision, hash sets), accounting, operations hash helpers, and terminal coloring.

Risks: Comparison policy has many interacting flags; a small change can alter listing format, delta detection, and sync equality differently. Blank hashes are treated as inconclusive rather than different. `--download-hash` may use large bandwidth and skips unknown-size objects. `--slow-hash-sync-only` intentionally makes listing and sync comparison differ.

Test signals: Existing scenarios `compare_all`, `nomodtime`, `ignorelistingchecksum`, `equal`, and backend matrix runs exercise this. Focused tests should cover `--compare` exclusions, no common hash fallback, slow hash combinations, unknown sizes, unsupported modtime, and download-hash first-use/error behavior.
