# File Research: sources/os/plan9/9front/sys/src/cmd/mk/archive.c

Handles archive-member targets of the form `archive(member)` for `mk`.

Key behavior:
- `atimeof()` splits archive/member names, caches aggregate archive scan times, refreshes member timestamps when the archive changes, and truncates long member names to archive header size.
- `atouch()` creates missing archives with `ARMAG` or updates an existing member timestamp in-place.
- `atimes()` scans Plan 9 ar headers, normalizes member mtimes, and stores `archive(member)` timestamps in the symbol table.
- `type()` recognizes archive files and warns once when a missing file is assumed to become an archive.
- `split()` parses and validates archive/member syntax.

Important dependencies: `mk.h`, `<ar.h>`, `SARMAG`, `SAR_HDR`, `SARNAME`, `S_TIME`, `S_AGG`, `S_BITCH`.

Notable risks:
- Only classic fixed-name archive headers are handled; long names are truncated.
- Direct header timestamp rewriting uses archive layout constants and seeks.
