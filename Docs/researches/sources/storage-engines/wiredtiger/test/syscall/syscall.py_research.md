# sources/storage-engines/wiredtiger/test/syscall/syscall.py

## Purpose

`syscall.py` is the command-line runner for WiredTiger syscall durability tests. It runs test executables under `strace` on Linux or `dtruss` on Darwin and compares captured system calls with preprocessed `.run` templates.

## Important APIs, Types, and Functions

Major types are `VariableContext`, `TestReturnCode`, `FileLine`, `Reader`, `FileReader`, `PreprocessedReader`, `HeadOpts`, `Runner`, and `SyscallCommand`. Important functions include `simplify_path`, `printfile`, `Runner.init`, `Runner.run`, `Runner.match_lines`, `Runner.match`, `Runner.call_compare`, argument/expression matching helpers, and `SyscallCommand.build_system_defines`.

## Control Flow

The script locates a usable WiredTiger build, parses CLI options, probes system macro values by compiling a small C program, discovers `.run` files, preprocesses each run file with `cc -E`, reads `SYSTEM`, `TRACE`, and `RUN` headers, runs the target executable under the tracer, and linearly matches trace output with fuzzy `...`, variable binding, `ASSERT_*`, and `OUTPUT` expectations.

## State and Persistence Behavior

It creates `WT_TEST.*` execution directories under the build syscall tree, writes stdout/stderr traces, optionally preserves failed or requested runs, and deletes successful scratch directories unless `--preserve` is set. It also temporarily creates `syscall_probe.c` and `syscall_probe`.

## Dependencies and Integration Points

Depends on `strace`, `dtruss`, `cc`, WiredTiger generated headers, `.run` files, CTest skip code 3 for environment issues, and built executables named `test_<directory>`.

## Risks and Edge Cases

Trace output is platform- and libc-sensitive, so templates need fuzzy matching. The `str_match` fuzzy branch appears to compare `s2.startswith(s2)`, which is tautological and may weaken matching for right-fuzzy strings. Environment issues such as macOS SIP are converted to skip.

## Test Signals

Signals include successful macro probe, successful target run, empty target stdout unless `OUTPUT` is expected, complete trace/template match, and preserved diagnostics on failure.
