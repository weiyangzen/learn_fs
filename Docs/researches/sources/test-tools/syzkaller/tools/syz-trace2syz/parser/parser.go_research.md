# sources/test-tools/syzkaller/tools/syz-trace2syz/parser/parser.go

## Purpose
This file provides the public byte-slice parsing loop for strace data, producing a `TraceTree` from generated lexer/parser components.

## Important APIs, types, and functions
- `parseSyscall` creates a `Stracelexer` for the current scanner line, calls `StraceParse`, and returns parser status plus parsed syscall.
- `shouldSkip` filters known non-syscall strace noise such as `ERESTART`, signal lines, and ptrace errors.
- `ParseData` scans input line by line, parses calls, inserts them into a `TraceTree`, and returns nil for empty traces.

## Control flow
`ParseData` creates a scanner with a 64 MiB max token buffer, skips known noisy lines, logs each scanned call at verbosity 4, parses the scanner's current bytes, fails on parse errors or nil calls, and accumulates calls in tree order. Scanner errors are returned after the loop.

## State and persistence behavior
All state is in-memory. The function does not read from or write to files; callers provide raw data.

## Dependencies and integration points
Uses generated `newStraceLexer` and `StraceParse`, local IR types, and `pkg/log`. It is the parser entry point consumed by syz-trace2syz conversion logic and parser tests.

## Risks and edge cases
Line-by-line parsing cannot handle syscall records split in ways other than the supported `<unfinished ...>`/`<... resumed>` format. `shouldSkip` is substring-based and may skip unusual legitimate lines containing those markers. Any parse failure aborts the whole input rather than collecting partial traces.

## Test signals
`parser_test.go` directly exercises `ParseData` for basic calls, return values, paused/resumed syscalls, PIDs, clone process trees, expressions, and group arguments.
