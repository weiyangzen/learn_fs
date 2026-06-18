# sources/storage-engines/tikv/scripts/check-license

## Purpose
Checks newly added, untracked Rust files for the required TiKV Apache-2.0 copyright header on the first line.

## Important Commands and Control Flow
The script uses `git ls-files -o --exclude-standard | grep "\.rs"` to find untracked Rust files, then uses a first-line `sed` match for `Copyright [year] TiKV Project Authors. Licensed under Apache-2.0.` A missing match prints the file path and exits 1; success prints `License check passed.`

## State, Dependencies, Integration
The script is read-only and depends on Git and sed. It is a pre-commit or CI-style guard for newly created Rust files, not a full repository audit.

## Risks and Test Signals
Tracked files are not checked. The regex is exact and first-line only, so alternative valid forms fail. Create untracked Rust files with and without the header to verify behavior.
