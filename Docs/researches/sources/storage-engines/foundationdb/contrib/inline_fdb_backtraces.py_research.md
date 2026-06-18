# sources/storage-engines/foundationdb/contrib/inline_fdb_backtraces.py

## Purpose
`inline_fdb_backtraces.py` post-processes FoundationDB trace output. It echoes each input line and, when it finds an embedded `addr2line` command with hexadecimal addresses, runs `llvm-addr2line` against a debug binary to inline symbolicated stack frames.

## Important APIs, Types, And Functions
`main()` defines CLI arguments: optional input `file`, `--addr2line`, `--debug-binary`, and `--dry-run`. The compiled regex matches `addr2line -e <binary> -p -C -f -i` followed by one or more `0x...` addresses. Symbolication uses `subprocess.run(cmd, capture_output=True, text=True, timeout=30)`.

## Control Flow
The script opens the requested file or reads stdin. For each line, it writes the original line to stdout, scans for matching address lists, builds a command from the configured addr2line binary and debug binary, and either prints the command in dry-run mode or executes it. Output is wrapped between `BACKTRACE BEGIN` and `BACKTRACE END` markers. Missing addr2line exits with status 1; timeouts are reported and processing continues.

## State And Persistence Behavior
The script has no persistent state. It streams input and output line by line, only holding regex matches and subprocess output for each backtrace.

## Dependencies And Integration Points
It depends on Python stdlib modules `argparse`, `re`, `subprocess`, and `sys`, plus an external addr2line-compatible binary and matching FoundationDB debug executable. It integrates with trace lines that already contain addr2line command text.

## Risks And Edge Cases
The default debug binary name is version-specific. The regex accepts lowercase hex only and ignores uppercase `0X` forms. It discards the binary path from the matched trace and always uses `--debug-binary`, which is intentional but can surprise users. It does not use a context manager for the optional input file. Subprocess stderr is printed only for nonzero exits.

## Test Signals
Tests can feed synthetic lines via stdin, run `--dry-run`, and assert original lines plus wrapper markers. Mocked subprocess tests should cover successful output, nonzero stderr, timeout, missing binary, multiple matches on one line, and no-match pass-through.
