# sources/distributed-fs/xrootd/src/XrdCl/XrdClFS.cc

## Purpose
Implements the `xrdfs` command-line client. It parses batch or interactive commands and maps them to synchronous `FileSystem`, `File`, copy, and operation-pipeline calls.

## Important APIs, Types, And Functions
Important helpers include `BuildPath`, `ConvertMode`, directory-list formatting helpers, `ProcessStatQuery`, `ProgressDisplay`, `CreateExecutor`, `ExecuteCommand`, `ExecuteInteractive`, `BuildPrompt`, `getArguments`, and `main`. Registered commands include `cache`, `cd`, `chmod`, `ls`, `help`, `stat`, `statvfs`, `locate`, `mv`, `mkdir`, `rm`, `rmdir`, `query`, `truncate`, `prepare`, `cat`, `tail`, `spaceinfo`, and `xattr`.

## Control Flow
`main` handles help, `--no-cwd`, URL validation, interactive mode, or batch command dispatch. `CreateExecutor` creates an `FSExecutor`, initializes `CWD=/`, and registers command handlers. Interactive mode reads commands with readline or fallback stubs, supports multiline quoted input, stores history, and executes through `FSExecutor`. Each `Do*` handler validates arguments, resolves paths via `BuildPath`, invokes the matching `FileSystem`/`File`/copy API, logs failures, prints user-facing output, and returns an `XRootDStatus` shell code.

## State And Persistence
Per-session state is held in the executor env: `CWD`, `NoCWD`, and `ServerURL`. Interactive mode persists command history in `$HOME/.xrdquery.history`. Commands mutate remote filesystem state for mkdir, rmdir, rm, mv, chmod, truncate, prepare/cache operations, xattrs, and copy outputs. `cat -o` writes local files via `CopyProcess`.

## Dependencies And Integration Points
Depends on `FileSystem`, `FileSystemUtils`, `FSExecutor`, `URL`, `Log`, `DefaultEnv`, `Utils`, `CopyProcess`, `File`, declarative operations, `ParallelOperation`, readline/ncurses when available, and Xrd utility formatting/error helpers. CMake builds it into the `xrdfs` executable together with `XrdClFSExecutor.cc`.

## Risks
Many argument parsers are hand-written and inconsistent. `DoLocate` indexes `path[0]` even if no path was provided. `DoCD` leaks `StatInfo` when the stat target is not a directory. `DoQuery` shadows `strArg` inside the non-prepare branch, so path normalization for checksum/xattr queries may not affect the outer string sent to the server. `DoTail` leaks `StatInfo`, ignores close status, and can loop forever in follow mode. `DoXAttr` assumes result vectors contain a front element on OK status. `BuildPath` rejects attempts to walk above root but can produce duplicate slash behavior depending on input.

## Test Signals
Useful tests include CLI help and URL validation, batch dispatch unknown-command status, `BuildPath` relative/absolute/dot-dot/no-cwd cases, `ConvertMode` validation, quoted interactive parsing, command argument matrix tests, mocked `FileSystem` output for stat/list/query/xattr, regression tests for empty locate path and query path normalization, and integration tests against a local xrootd server for filesystem mutations.
