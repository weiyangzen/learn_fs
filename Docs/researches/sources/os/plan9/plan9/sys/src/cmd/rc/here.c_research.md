# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/here.c

Here-document creation, reading, substitution, and cleanup for rc.

Main logic:
- `heredoc()` records a pending heredoc tag and returns a temporary filename token.
- Temporary names are generated under `/tmp/here....` using pid and a serial number.
- `readhere()` reads heredoc bodies after compilation, writes them to temp files, performs substitution unless the tag was quoted, emits cleanup code via `cleanhere()`, and frees pending records.
- `psubst()` expands `$name`, `$n`, and `$$` in heredoc lines.
- `pstrs()` prints word lists with spaces.

Risk/notes:
- The file notes a known bug: lines longer than `NLINE` are split, which can affect EOF marker recognition and substitution.
- Heredoc cleanup is compiled into the command stream as `Xdelhere`.
