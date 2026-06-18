# sources/sync-backup/restic/cmd/restic/cmd_stats.go

Purpose: implements `restic stats`, walking snapshots or raw blobs to report repository size/count statistics in several counting modes.

Important APIs/types/functions: `StatsOptions`; `runStats`; `statsWalkSnapshot`; `statsWalkTree`; `makeFileIDByContents`; `verifyStatsInput`; `statsContainer`; count-mode constants; debug helpers; `sizeHistogram`.

Control flow and state: validates mode, opens read lock, memoizes snapshots, loads index, optionally runs debug histograms. Normal flow collects filtered snapshots, creates progress, walks each snapshot. `restore-size` counts restored file sizes with hardlink de-duplication; `files-by-contents` hashes content blob sequences; `blobs-per-file` counts unique blob references per path; `raw-data` uses `data.FindUsedBlobs` then looks up ciphertext and uncompressed sizes. Output is JSON `statsContainer` or text summary. No repository mutation occurs.

Dependencies and integration points: uses walker, restorer hardlink index, repository blob lookup, chunker/repository size limits for histograms, stats UI progress, and table rendering.

Risks: `makeFileIDByContents` only considers content IDs, so metadata differences are ignored by design. Raw-data compression metrics depend on repo version and index metadata. Blob lookup failures abort. Debug mode is accepted but not listed in public shell completion.

Test signals: stats unit tests cover histogram construction, bucket insertion/oversized values, and string formatting.
