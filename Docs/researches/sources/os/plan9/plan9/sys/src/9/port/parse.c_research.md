# File Research: sources/os/plan9/plan9/sys/src/9/port/parse.c

Provides small command parsing helpers used by device control files.

Key functions:
- `parsecmd(char *p, int n)`: copies an input buffer, strips one trailing newline, tokenizes whitespace-separated fields, and returns a `Cmdbuf` containing the original buffer and `char **f` field vector.
- `cmderror(Cmdbuf *cb, char *s)`: reconstructs the command with `%q` quoting and raises an error with diagnostic text.
- `lookupcmd(Cmdbuf *cb, Cmdtab *ctab, int nctab)`: matches `cb->f[0]` against a command table, supports wildcard `"*"`, verifies argument count when `narg != 0`, and reports unknown/argument errors.

Implementation notes:
- `ncmdfield` computes a conservative number of token slots by scanning whitespace.
- Allocation is a single `smalloc` containing `Cmdbuf`, field pointers, and copied command text.
- If running in a process context, `parsecmd` protects allocation/copy with Plan 9 error unwinding.

Role:
- Shared parser for kernel device control messages.
