<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/internal/build_csv/main.go -->
# sources/user-network-fs/rclone/cmd/test/info/internal/build_csv/main.go

Source read: complete file, 158 lines, 3922 bytes, sha256 `2682cf698135590806c37dbfa264ce1933ad5c00a3aa2eeaae52a3742a9e5e55`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/info/internal/build_csv/main.go_research.md`.

## Purpose
Converts multiple `rclone test info` JSON reports into a comparative CSV matrix for control-character behavior.

## Important APIs, types, and functions
`main` parses `-o`, reads each JSON file into `internal.InfoReport`, builds sorted remote/character axes, maps write/get/list results to compact codes, and writes CSV. Helpers `sok` and `pok` convert errors/presence values.

## Control flow
Input files are decoded, reports lacking ControlCharacters are skipped, headers are generated in three rows, rows are emitted per character, and output goes to stdout or a created file.

## State and persistence behavior
Persistent state is the output CSV file when `-o` is not `-`. Inputs are read-only.

## Dependencies and integration points
Depends on CSV/JSON stdlib, sorted maps, strconv quoting, internal report types, and rclone fatal logging.

## Risks and edge cases
Only handles reports with control-character data; other info fields are ignored. Fatal logging exits on malformed inputs or write errors.

## Test signals
Used manually after collecting info JSON outputs to compare providers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/internal/build_csv/main.go -->
