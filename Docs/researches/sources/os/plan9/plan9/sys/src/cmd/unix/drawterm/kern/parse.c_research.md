# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/parse.c

Implements common control-message parsing helpers.

Key behavior:
- `parsecmd` counts whitespace-separated fields, allocates one `Cmdbuf` containing metadata, field pointer array, and a NUL-terminated copy of the input.
- Strips a trailing newline before tokenization.
- Uses `tokenize` to populate `cb->f` and `cb->nf`.
- `cmderror` reconstructs a quoted command for diagnostics and raises an error.
- `lookupcmd` matches a parsed command against a `Cmdtab`, validates argument count, supports wildcard command `"*"`, and reports unknown commands.

Used by:
- `devcons.c` for reboot control.
- `devaudio.c` for volume control.
- `devtls.c` and other control-file parsers.

Notable risks:
- Parsing is whitespace-only; quoting is not preserved as command syntax, only used in reconstructed error text.
