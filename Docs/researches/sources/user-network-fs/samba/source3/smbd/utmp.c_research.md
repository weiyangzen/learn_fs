# sources/user-network-fs/samba/source3/smbd/utmp.c

## Purpose
Reflects Samba connection claim/yield events into platform utmp/wtmp or utmpx/wtmpx accounting files when compiled with `WITH_UTMP`. Provides no-op stubs otherwise.

## Important APIs, Types, and Functions
Exports `sys_utmp_claim()` and `sys_utmp_yield()`. Internal helpers include `uw_pathname()` for configured/default file paths, `utmp_nox_update()` for utmp/wtmp APIs, `sys_utmp_update()` for utmpx-preferred updates, `utmp_strcpy()` for fixed-size fields, `ut_id_encode()` for four-byte IDs, and `sys_utmp_fill()` for portable struct population.

## Control Flow
Without `WITH_UTMP`, claim/yield immediately return. With utmp enabled, claim/yield zero a `struct utmp`, set user/dead process type where available, fill username, host, line, pid, timestamp, and encoded ID, then call `sys_utmp_update()`. The update path prefers utmpx only when all required APIs and paths are available; otherwise it falls back to utmp/wtmp. Wtmp without `updwtmp()` appends records directly and truncates back on partial writes.

## State and Persistence
Writes OS accounting files selected by `lp_utmp_directory()` and `lp_wtmp_directory()` or platform defaults such as `UTMP_FILE`/`WTMP_FILE`/`UTMPX_FILE`/`WTMPX_FILE`. The ID encodes Samba's session number into utmp's constrained `ut_id` field.

## Dependencies and Integration Points
Depends on configure-time platform feature macros, utmp/utmpx headers, Samba loadparm directories, time helpers, debug logging, and smbd session accounting callers. It integrates with Unix tools such as `who`/`last` indirectly through accounting files.

## Risks
The file is highly platform-conditional; unsupported combinations silently fall back or log low-level warnings. Direct wtmp append has limited locking semantics. Fixed-size string fields truncate without multibyte awareness. The 4-byte ID encoding intentionally ignores overflow because input is effectively random/session-derived.

## Test Signals
Build with and without `WITH_UTMP`, with utmp-only and utmpx-capable feature sets. Test custom utmp/wtmp directories, login/logout record content, hostname truncation, ID uniqueness across many session numbers, and fallback when default utmpx paths are empty.
