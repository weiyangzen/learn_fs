# File Research: sources/os/plan9/9front/sys/src/cmd/nm.c

Plan 9 `nm` implementation for object files, archives, and executables.

Key elements:
- Supports flags `-a`, `-g`, `-h`, `-n`, `-s`, `-T`, and `-u`.
- Opens each file, detects archives with `isar`, object files with `objtype`, and executables with `crackhdr`/`syminit`.
- `doar` iterates archive members, skipping `__.SYMDEF`.
- `psym` filters symbols according to type and flags.
- `zenter` builds filename-element translation for `z` records.
- `printsyms` sorts by name or numeric value, prints optional file prefix, optional type signature, address, type, and name/path.
- Errors are accumulated into exit status `"errors"`.

Notable behavior:
- `-s` preserves original symbol order.
- Width expands from 8 to 16 hex digits when a symbol value exceeds 32 bits.
- Hidden dot/dollar symbols are omitted unless `-a`.

Risks and quirks:
- Comment notes sorting can mishandle `z` records with `-a`.
- Global `filename` is temporarily changed to archive member names.
