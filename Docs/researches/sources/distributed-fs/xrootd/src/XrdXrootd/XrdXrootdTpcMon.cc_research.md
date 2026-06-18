# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTpcMon.cc

## Purpose

This file emits third-party-copy monitoring records as JSON lines into an `XrdXrootdGStream`. It normalizes local path specs into full URLs, formats timestamps, and reports copy direction, protocol, client, streams, IP family, return code, and size.

## Important APIs, types, and functions

The constructor initializes logging and captures `XRDHOST[:XRDPORT]` into a static `hostport`. `getURL()` converts path-like specs into `<protocol>://<hostport>/<path>`. `getUTC()` formats `timeval` as UTC ISO-like strings. `Report()` builds JSON from `TpcInfo` and inserts it into `gStream`.

## Control flow

TPC code fills `TpcInfo`, including begin/end times and URLs, then calls `Report()`. `Report()` resolves source/destination display URLs, formats begin/end timestamps, builds a JSON object with push/pull and IPv4/IPv6 indicators, warns if truncated, and inserts the null-terminated message into the stream.

## State and persistence behavior

`hostport` is static process memory initialized from environment and intentionally leaked for process lifetime. Reports are transient inserts into `XrdXrootdGStream`; persistence depends on the configured stream consumer.

## Dependencies and integration points

The file depends on `XrdSysError`, `XrdXrootdGStream`, and `XrdXrootdTpcMon`. It is configured from monitoring setup and used by TPC transfer paths.

## Risks and edge cases

`getURL()` produces `protocol://hostport//path` for a path beginning with `/` because the format includes `/%s`; this may be intended by existing consumers but should be checked. JSON strings are not escaped, so quotes or control characters in client IDs or URLs can produce invalid JSON. Timestamp milliseconds use `tv_usec` directly with `%03u`, which prints microseconds as at least three digits rather than dividing to milliseconds.

## Test signals

Tests should cover env-derived hostport, local path URL normalization, external URL pass-through, UTC formatting, truncation warning, gStream rejection warning, JSON escaping expectations, and push/pull plus IP-family flags.
