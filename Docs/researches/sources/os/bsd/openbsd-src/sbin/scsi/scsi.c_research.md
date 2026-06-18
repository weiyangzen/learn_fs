# File Research: sources/os/bsd/openbsd-src/sbin/scsi/scsi.c

This file implements the `scsi` command-line utility for raw SCSI commands, kernel SCSI debug control, and mode page display/editing.

Key APIs:
- `main()`: dispatches debug setting, raw command execution, or mode page handling.
- `procargs()`: parses `-f`, `-d`, `-c`, `-m`, `-e`, `-P`, `-s`, and `-v`.
- `do_cmd()`: builds a SCSI CDB from a format string and arguments, optionally handles `-i` data-in or `-o` data-out phases, submits the request, and decodes/writes returned data.
- `mode_sense()`, `mode_select()`: issue SCSI mode sense/select commands.
- `mode_lookup()`: reads `/usr/share/misc/scsi_modes` or `$SCSI_MODES` for mode page format descriptions.
- Mode editor helpers: create a temp file, decode editable/default/current values, invoke `$VISUAL`/`$EDITOR`/`vi`, re-encode edited values, and send mode select.
- `iget()`, `cget()`, `arg_put()`: argument and decoded-field callbacks used by `libscsi`.

Behavior and integration:
- Uses `SCIOCDEBUG` for kernel SCSI debugging and `SCIOCCOMMAND` through `libscsi`.
- Supports raw binary stdin/stdout with `-` as data format.
- Mode editing first reads changeable values, then defaults/current values, then lets the user edit named fields.
- Temporary edit files are created under `/var/tmp` with `mkstemp()` and cleaned by `atexit()`.

Risk notes:
- This utility can send arbitrary SCSI commands and mode selects to devices; misuse can change or damage device state.
- Mode database parsing uses a fixed 1024-byte format buffer and a fixed 64-entry edit table.
- The editor is launched through `/bin/sh -c`, using the selected editor string plus temp pathname.
