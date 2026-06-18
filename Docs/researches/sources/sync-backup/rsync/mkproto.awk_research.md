# sources/sync-backup/rsync/mkproto.awk

## Purpose
`mkproto.awk` generates `proto.h` from rsync C sources. It extracts function declarations and generated accessor prototypes, preserving an existing file when content has not changed.

## Important APIs, Types, and Functions
The AWK script has `BEGIN`, pattern-action blocks, and `END`. It reads existing `proto.h` into `old_protos`, accumulates `protos`, recognizes `FN_LOCAL_*` and `FN_GLOBAL_*` macro invocations, skips static/extern/semicolon/non-function lines, handles single-line and multi-line function headers, and touches `proto.h-tstamp`.

## Control Flow
In `BEGIN`, it loads current `proto.h` and seeds the generated warning comment. While scanning input, `inheader` mode appends continued function prototype lines until a line ending in `)` is seen, then appends a semicolon. `FN_*` lines are rewritten from macro declarations into actual `lp_*` prototypes, mapping `BOOL`, `CHAR`, `INTEGER`, and `STRING` wrapper syntax to C types and selecting `(int module_id)` for local accessors or `(void)` for globals. Ordinary function headers are appended with semicolons. In `END`, it writes `proto.h` only if content changed and always touches `proto.h-tstamp`.

## State and Persistence
Persistent outputs are `proto.h` and `proto.h-tstamp`. In-memory state is limited to `old_protos`, `protos`, and `inheader`.

## Dependencies and Integration Points
The script is run by `make proto` or old build flows and consumes C source concatenation. It is aware of rsync's loadparm accessor macro naming and keeps generated prototypes in sync with implementation files.

## Risks
The parser is intentionally heuristic. It can miss nonstandard formatting, function pointer declarations, attributes, or return types that do not match the expected leading identifier pattern. It skips all `static` functions, which is intended for public prototypes. Changing accessor macros requires updating this script.

## Test Signals
Tests should feed representative C functions, multi-line prototypes, skipped static and extern declarations, `FN_LOCAL_*` and `FN_GLOBAL_*` accessors of every supported type, unchanged-output no-op behavior, and timestamp creation.
