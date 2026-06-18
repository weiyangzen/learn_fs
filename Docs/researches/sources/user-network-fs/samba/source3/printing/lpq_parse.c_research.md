# sources/user-network-fs/samba/source3/printing/lpq_parse.c

## Purpose
`lpq_parse.c` parses textual queue output from multiple Unix and network printing systems into Samba `print_queue_struct` and `print_status_struct` values. It normalizes vendor-specific `lpq`/`lpstat` formats so the rest of Samba can reason about job id, owner, file/document name, size, priority, time, and status consistently.

## Important APIs, types, and functions
- `parse_lpq_entry(printing_type, line, buf, status, first)` is the exported dispatcher.
- Format-specific parsers include `parse_lpq_bsd`, `parse_lpq_lprng`, `parse_lpq_aix`, `parse_lpq_hpux`, `parse_lpq_sysv`, `parse_lpq_qnx`, `parse_lpq_plp`, `parse_lpq_nt`, and `parse_lpq_os2`.
- Developer builds add `parse_lpq_vlp` for virtual/test printer output.
- `EntryTime` parses month/day/time fields and adjusts previous-year jobs; `LPRng_time` parses LPRng time strings in short and full-date forms.
- Status keyword arrays classify non-job lines as OK, stopped, or error messages.

## Control flow
`parse_lpq_entry` switches on `enum printing_types`, invokes one parser, strips the newline from the input line, and if no job was parsed, optionally treats the line as a printer status line by lowercasing it and matching severity keyword sets. Most parsers tokenize with `next_token_talloc` or `strtok_r`, validate minimum token counts and numeric columns, then fill `print_queue_struct`. Some formats need special handling: HPUX stores static header-line state and returns a job only after a following indented file line; NT and OS/2 parse fixed-width output; SYSV rewrites only the last dash before the job id; LPRng removes `@host` from owner names.

## State and persistence behavior
The parser has little persistent state, but `parse_lpq_hpux` uses static variables to carry the current header line, user, job id, priority, time, status, and base priority across calls. Other parsers are stateless aside from mutating the input line in place for tokenization and normalization. Output state is written into caller-provided `print_queue_struct` and `print_status_struct`.

## Dependencies and integration points
The file depends on `printing.h` for queue/status structures, print status constants, and `enum printing_types`, plus Samba string wrappers and talloc tokenization helpers. It is used by printing backends that execute platform-specific queue commands and need to populate Samba's print queue cache.

## Risks and edge cases
- Parsers mutate the input line, so callers must pass writable buffers.
- Fixed-width NT/OS2 parsers reject lines with unexpected lengths, making them sensitive to localization or server version changes.
- The HPUX parser's static state can be wrong if multiple queues are parsed interleaved in one process.
- Many sizes are parsed with `atoi` into integer fields and may truncate or overflow on very large jobs.
- Status-line matching uses substring checks after lowercasing and may misclassify localized messages or lines containing coincidental keywords.
- Filename handling often collapses paths to basenames or substitutes `STDIN`, which can lose document detail.

## Test signals
Good tests feed representative queue outputs for each `PRINT_*` type, including header lines, malformed numeric fields, filenames with spaces, standard-input markers, LPRng host-qualified users, HPUX two-line jobs, status-only lines, and developer VLP records. Regression tests should verify `print_status_struct` severity does not downgrade once an error has been observed.
