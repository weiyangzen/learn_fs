# File Research: sources/local-fs/jfsutils/libfs/log_read.c

This file implements low-level JFS journal page reading for log replay. It owns the 4-page journal buffer cache state (`nextrep`, `logptr[]`, `logp[]`) and exports helpers used by `logredo.c` to find the logical end of the circular log and read records backward.

Main functions:
- `findEndOfLog()` binary-searches log pages 2 through `Log.size - 1` for the highest page sequence/eor pair, handles wrapped page numbers, and backs off from partial long records whose chosen page has only the log page header.
- `pageVal()` loads a page and normalizes it through `setLogpage()`.
- `getLogpage()` returns a cached log page or reads it from `Log.fp`, using `Log.xaddr` only for inline logs.
- `setLogpage()` reconciles mismatched page header/trailer values after interrupted writes, choosing the older/smaller page/eor state, and writes the corrected page back.
- `logRead()` reads one log record descriptor plus optional data from a backward log address, validates record length against a two-page buffer, swaps the descriptor, and returns the address of the previous record.
- `moveWords()` copies 32-bit words backward across log page boundaries, wrapping from page 2 back to the last data page.

Integration points:
- Depends on `Log` and `vopen[]` from `logredo.c`, log layout from `jfs_logmgr.h`, endian helpers, disk I/O through `ujfs_rw_diskblocks()`, and message logging via `fsck_send_msg()`.
- Error paths return `JLOG_*`, `READLOGERROR`, or logredo negative codes from `logredo.h`.

Important invariants:
- Log page 0 is unused and page 1 is the log superblock; replay data starts at page 2.
- `lognumread > Log.size - 2` is treated as log wrap/corruption.
- `ld->aggregate > MAX_ACTIVE` is normalized to 0 for legacy log records that encoded a device number.

Risks and notes:
- `setLogpage()` always writes corrected pages at `Log.xaddr + LOGPNTOB(pno)`, while `getLogpage()` only adds `Log.xaddr` for inline logs. If `setLogpage()` is called for an external log with `Log.xaddr == 0`, this is harmless, but the asymmetry is worth preserving deliberately.
- `moveWords()` updates `*offset` by `4 * nwords` after the second-page copy, where `nwords` is the remaining requested count, not necessarily the number actually copied on the final iteration. This works for the expected record/page constraints but is fragile code.
