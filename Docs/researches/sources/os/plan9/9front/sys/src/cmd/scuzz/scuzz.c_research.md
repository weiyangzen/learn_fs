# File Research: sources/os/plan9/9front/sys/src/cmd/scuzz/scuzz.c

Purpose: Interactive SCSI command shell and utility.

Major areas:
- Global transfer buffer and options: `maxiosize`, `exabyte`, `force6bytecmds`, `verbose`.
- File/pipeline I/O: `mkfile` supports direct files or `|command` pipes for read/write commands.
- Command handlers: readiness, rewind, request sense, format, read/write, seek, filemark/space, inquiry, mode sense/select, start/stop/eject/ingest, capacity, CD-R/MMC commands, CD audio, changer commands, probe/open/close/help.
- Decoders: prints mode pages, TOC/PMA/session data, disc info, track info, CD mechanism status, changer element status.
- Parser: `tokenise` and `parse` support shell-like single quotes with doubled embedded quotes.
- Main loop: optionally opens an initial target, reads commands from stdin, dispatches through `scsicmd[]`, prints `ok` or status/sense diagnostics.

Integration: Command table calls all `SR*` helpers across `scsireq.c`, `cdr.c`, `cdaudio.c`, `changer.c`, and `sense.c`.

Risks:
- Many decoders assume response buffers contain enough bytes for the fields printed.
- Some older CD-R commands are compiled but commented out of the command table.
- `cmdmodesense10` leaks `list` if `SRmodesense10` fails before `free`.
- Destructive commands are available interactively with limited safeguards.
