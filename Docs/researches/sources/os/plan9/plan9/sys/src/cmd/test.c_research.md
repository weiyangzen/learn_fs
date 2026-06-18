# File Research: sources/os/plan9/plan9/sys/src/cmd/test.c

Plan 9 implementation of POSIX `test` and `[`, with Plan 9 file-mode extensions.

Key responsibilities:
- Parses recursive expressions with precedence for `-o`, `-a`, `!`, and parentheses.
- Implements string tests, integer comparisons, file existence/access tests, type tests, tty tests, and timestamp comparisons.
- Adds Plan 9 tests `-A` append-only, `-L` exclusive-use, and `-T` temporary.
- Uses `dirstat`, `dirfstat`, `access`, and Plan 9 mode bits.

Important behavior:
- `[` mode requires the final argument to be `]`.
- `-t` defaults to fd 1 if no fd argument is provided.
- `-older` accepts absolute or relative time syntax with suffixes `y`, `M`, `d`, `h`, `m`, `s`.
- `-ot` and `-nt` are implemented by reversed helper calls so the final semantics match shell expectations.

Notable risks:
- Some POSIX primaries (`-c`, `-b`, `-u`, `-g`) are present but always return false.
- The post-parse unexpected-token check is disabled because short-circuit operators may leave unconsumed arguments.
