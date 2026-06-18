<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/info.go -->
# sources/user-network-fs/rclone/cmd/test/info/info.go

Source read: complete file, 515 lines, 15058 bytes, sha256 `16b948420baef0886b3e1891346292821750ca1d9959f602d349328d7883a7f2`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/info/info.go_research.md`.

## Purpose
Implements `rclone test info`, a diagnostic command that probes backend filename/control-character limits, Unicode normalization behavior, streaming upload support, maximum filename lengths, and writes JSON reports.

## Important APIs, types, and functions
`results` captures remote name, control character maps, max lengths, normalization flags, streaming flag, base32768 flag, context, and Fs. Important methods include `newResults`, `Print`, `WriteJSON`, `checkControls`, `findMaxLength`, `checkUTF8Normalization`, `checkStreaming`, and `readInfo`.

## Control flow
Command flags select which probes run. Control checks create filenames with special characters in left/middle/right positions, attempt write/get/list operations, and record errors/presence. Length checks binary-search-ish increasing names. Normalization and base32768 checks sync/check generated local files. Streaming writes an unknown-size object and validates hashes/size.

## State and persistence behavior
The command creates and removes temporary remote test files/directories unless `--keep-test-files` is set. Results are printed and optionally written as JSON for later CSV aggregation.

## Dependencies and integration points
Depends on rclone Fs operations, sync/check/purge, object info, hash verification, Unicode normalization helpers, JSON encoding, and internal report types.

## Risks and edge cases
It intentionally mutates the target remote and can leave test files if interrupted or keep mode is enabled. Results are provider and account dependent. Some checks are expensive and may hit filename, API, or rate limits.

## Test signals
Manual diagnostic output plus `internal/build_csv` aggregation provide test signals; no conventional unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/info.go -->
