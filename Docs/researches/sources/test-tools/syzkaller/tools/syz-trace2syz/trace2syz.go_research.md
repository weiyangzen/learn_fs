# sources/test-tools/syzkaller/tools/syz-trace2syz/trace2syz.go

## Purpose

`trace2syz.go` is the command-line tool that converts one strace file or a directory of strace files into a syzkaller `corpus.db`. It can also write serialized programs for inspection.

## Important APIs, Types, and Functions

The tool defines flags `-file`, `-dir`, and `-deserialize`, constants for Linux/amd64 target selection, and functions `main`, `initializeTarget`, `parseTraces`, `getTraceFiles`, and `pack`. It uses `proggen.ParseFile`, `db.Create`, `osutil.WriteFile`, and `prog.Target`.

## Control Flow

`main` parses flags, initializes the target and constant map, parses traces, and packs generated programs into `corpus.db`. `parseTraces` chooses either the single file or all directory entries, converts each file with `proggen.ParseFile`, optionally writes each serialized program into the deserialize directory, and returns all programs. `pack` serializes records into a syzkaller database.

## State and Persistence Behavior

It reads trace files and writes `corpus.db` in the current working directory. With `-deserialize`, it writes per-program text files named from the trace basename plus an index. It does not filter directory entries by type.

## Dependencies and Integration Points

The tool integrates strace output, `proggen`, syzkaller target descriptions, and corpus database creation. It is intended for seed selection and debugging, not as a general live tracer.

## Risks and Test Signals

Hard-coded Linux/amd64 support limits portability. Fatal errors stop the whole batch on one bad trace. Directory mode includes every entry and does not sort explicitly, so corpus generation order depends on `os.ReadDir` names. Tests should cover missing flags, unreadable files, parse failures, deserialize output, and database creation with multiple traces.
