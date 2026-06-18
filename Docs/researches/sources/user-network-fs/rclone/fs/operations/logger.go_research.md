# sources/user-network-fs/rclone/fs/operations/logger.go

## Purpose
`logger.go` implements reusable sync/check logging primitives. It maps operation outcomes to sigils and writers, stores logger functions/options in context, predicts post-sync destination winners, and formats `--dest-after` output through `ListFormat`/`ListJSON`.

## Important APIs, types, and functions
- `Sigil` and constants `MissingOnSrc`, `MissingOnDst`, `Match`, `Differ`, `TransferError`, and `Other` categorize sync outcomes.
- `LoggerFn` is the callback signature used by sync-like operations.
- `LoggerOpt` contains output writers, JSON/list formatting options, filters, and a destination-after listJSON instance.
- `NewDefaultLoggerFn`, `WithLogger`, `WithLoggerOpt`, `GetLogger`, `GetLoggerOpt`, `WithSyncLogger`, and `NewLoggerOpt` manage logging callbacks and default buffers.
- `Winner` and `WinningSide` infer which source or destination entry should exist after sync.
- `SetListFormat`, `NewListJSON`, `JSONEntry`, and `PrintDestAfter` produce formatted destination-after lines.

## Control flow
Default logging locks a mutex, ignores non-object pairs unless handling destination-after directory output, chooses a filename from source or destination, writes to the category writer and combined writer, and optionally prints the predicted destination-after state. `WinningSide` branches on sigil, dry-run, delete-mode-off, ignore/update config flags, directory errors, and transfer errors to choose `src`, `dst`, or no winner. `SetListFormat` maps format characters to `ListFormat` output functions and parallel `ListJSONOpt` settings.

## State and persistence behavior
State is stored in contexts and caller-owned buffers/writers. `NewLoggerOpt` initializes in-memory buffers for every output class. The logger itself does not mutate remote state, but its winner prediction depends on config and may read metadata/hash fields when formatting destination-after output.

## Dependencies and integration points
It integrates with `operations.ListFormat`, `ListJSONOpt`, and `listJSON`, `fs.ConfigInfo`, `fs.DirEntry`/`Object`, hash types, `pflag`, and synchronized output helpers. Sync and bisync use these APIs to capture combined result logs and destination-after inventories.

## Risks and edge cases
Winner prediction is approximate for max-duration hard cutoffs, compare/copy-dest, high-level retries, server-side directory moves, and some error cases. The default logger must avoid nil writer panics and must not emit directories as ordinary file entries. `errors.Is(err, errors.New(...))` in one branch cannot match a freshly allocated error, so deadline handling is the reliable path there.

## Test signals
This file has no dedicated test in this subset, but it is exercised indirectly by sync/copy/check tests that install loggers or inspect combined output. `check.go` has a separate reporting implementation with similar sigils, and `operations.go` calls logger callbacks from equality, transfer, deletion, and move/copy decisions.
