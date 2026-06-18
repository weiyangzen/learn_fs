# sources/storage-engines/lmdb/libraries/liblmdb/mplay.c

## Purpose
`mplay.c` replays text logs of LMDB API calls into live child processes, reconstructing environments, transactions, cursors, and data operations for debugging or deterministic reproduction.

## Important APIs, types, and functions
It defines mapping tables `envpair`, `txnpair`, `crspair`, and `pidpair` to translate logged pointer/process IDs to runtime LMDB objects. Lookup helpers add/find/delete environments, transactions, cursors, and child processes. `child` parses replay commands and executes LMDB APIs. `addpid`, `findpid`, `delpid`, and `reaper` manage forked workers. `main` dispatches input lines prefixed with process IDs.

## Control flow
The parent reads log lines, ignores non-command lines, creates a child per logged process ID, writes the LMDB call line to that child over a pipe, and waits for a one-byte acknowledgment. Each child parses commands such as environment create/open/close, transaction begin/commit/abort, DBI open/close, cursor open/put/delete, put, and delete. Hex-encoded keys and data are decoded into reusable buffers before LMDB calls. Logged process kill lines trigger child shutdown.

## State and persistence behavior
Replay creates and mutates actual LMDB environments named in the log. Transactions, cursors, and environments are tracked in fixed-size in-memory arrays. If logged data omits a value payload, generated data uses the current transaction ID text, making replay state partly synthetic.

## Dependencies and integration points
The tool depends on POSIX `fork`, `pipe`, `dup2`, `waitpid`, and signals, so it is not Windows-oriented. It integrates with LMDB's public C API and with log formats that print pointer values and hex payloads in the expected layout.

## Risks and edge cases
Fixed maxima of 16 environments, transactions, cursors, and child processes can assert on larger traces. Parsing is by `strncmp`, `sscanf`, and delimiter mutation, so malformed logs can crash. Signal handling and `killpid` coordination assume one child reap at a time. The tool can overwrite real database paths from logs.

## Test signals
Replay tests should cover multi-process traces, interleaved transactions and cursors, generated data paths, duplicate/notfound tolerances, child exit on env close, max-table assertions, and malformed or truncated command lines.
