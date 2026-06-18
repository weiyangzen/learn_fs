<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcBlacklistDecision.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcBlacklistDecision.cc

## Purpose

`XrdPfcBlacklistDecision.cc` implements a dynamic decision plugin that permits caching unless the logical filename matches one of the configured blacklist glob patterns.

## Important APIs, Types, And Functions

- `BlacklistDecision` derives from `XrdPfc::Decision`.
- `ConfigDecision(const char *parms)` treats `parms` as a blacklist file path, reads nonblank trimmed lines, and stores them in `m_blacklist`.
- `Decide(const std::string &lfn, XrdOss&) const` rejects paths where `fnmatch(pattern, lfn, FNM_PATHNAME)` succeeds.
- Exported `XrdPfcGetDecision(XrdSysError&)` returns a new `BlacklistDecision`.

## Control Flow

Configuration loading opens and parses the blacklist file at plugin setup time. Runtime decisions iterate the vector in file order and return false on the first match; otherwise they allow caching.

## State And Persistence

The plugin stores blacklist patterns in memory and logs configuration details. It reads but does not write the blacklist file.

## Dependencies And Integration Points

It depends on `XrdPfcDecision.hh`, `XrdSysError`, `fnmatch`, `stdio`, and `errno`. It integrates through `Cache::xdlib()` and the `XrdPfcGetDecision` symbol.

## Risks And Edge Cases

- Lines with leading whitespace are trimmed, but trailing spaces other than newline are kept as part of the pattern.
- Comment syntax is not supported; a line beginning with `#` becomes a real pattern.
- Parse errors after partial reads are logged but `ConfigDecision()` still returns true.
- Large blacklist files are stored entirely in memory and checked linearly per attach.

## Test Signals

Tests should cover missing parameter, unreadable file, blank and whitespace-only lines, newline trimming, `FNM_PATHNAME` behavior across slashes, first-match rejection, no-match allow, and parse-error logging behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcBlacklistDecision.cc -->
