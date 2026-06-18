<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOuca2x.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOuca2x.cc

## Purpose

`XrdOuca2x.cc` implements ASCII-to-value conversion utilities used by configuration parsers. It converts numeric strings, sizes, durations, percentages, ports, file modes, scaled decimals, and hex/binary data while logging consistent configuration errors through `XrdSysError`.

## Important APIs, Types, And Functions

- `a2i()` and `a2ll()` parse signed decimal integers with min/max checks.
- `a2fm()` parses octal file modes and maps user/group/other bits to `S_I*` masks.
- `a2p()` parses numeric ports, service names, and optional `any`.
- `a2sn()` parses scaled decimal values using caller-provided scale.
- `a2sp()` parses storage values or percentages, encoding percentages as negative values.
- `a2sz()` parses byte sizes with `k/m/g/t` binary suffixes.
- `a2tm()` parses durations with `s/m/h/d` suffixes.
- `a2vp()` parses values or percentages, also encoding percentages as negative values.
- `b2x()` and `x2b()` convert between binary bytes and lower-case hex text.
- Private `Emsg()` overloads format bound-check failures.

## Control Flow

Each parser validates presence, calls a C library conversion routine, checks `errno` and trailing characters, applies optional range limits, and returns `0` on success or `-1` on failure after logging. Suffix parsers treat a missing suffix as base units. The port parser uses `XrdNetUtils::ServPort()` for named services.

## State And Persistence

The file has no persistent state. It writes parsed values through caller-provided pointers and emits errors to the supplied `XrdSysError`.

## Dependencies And Integration Points

It depends on `XrdSysError`, POSIX mode bits, and `XrdNetUtils`. It is heavily used by XRootD config parsing, including `XrdPfcConfiguration.cc` for cache watermarks, RAM, block size, prefetch counts, purge intervals, checksum retention, and command test parameters.

## Risks And Edge Cases

- `a2fm()` uses `strtol(item, NULL, 8)`, so trailing non-octal text is not checked.
- `a2sp()` appears to check `if (*val > maxv)` twice; the second branch formats a "less than" error but should likely compare against `minv`.
- Percentage encodings as negative values require every consumer to know the convention.
- `a2tm()` multiplies a `strtoll()` result into an `int*`, so very large values depend on range checks and integer conversion behavior.
- `b2x()` returns `slen*2+1`, including the null terminator, unlike many length APIs.

## Test Signals

Tests should cover valid and invalid suffixes, min/max failures, service-name ports, `any` allowed/disallowed, percentage encoding, decimal scaled parsing, file-mode conversion, malformed octal text, odd-length hex with and without right adjustment, destination buffer too small, and the suspected `a2sp()` minimum-bound bug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOuca2x.cc -->
