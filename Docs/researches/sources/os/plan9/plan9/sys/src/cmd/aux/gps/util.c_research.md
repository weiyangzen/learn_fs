# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/gps/util.c

This file provides shared GPS coordinate formatting and parsing helpers.

Key behavior:
- Defines `nowhere`.
- Implements `%L` formatting for degrees/minutes/seconds with hemisphere suffixes.
- Parses latitude/longitude inputs with decimal or colon-separated degree/minute/second syntax.
- Supports explicit N/S/E/W suffixes and fallback positional latitude then longitude parsing.
- Contains an unused/static RTC correction helper.

Important details:
- Western longitude is made negative by default in the two-number fallback path.
- Duplicate lat or lon fields cause parse failure.

Filesystem relevance:
- Indirect support for GPS utilities and `gpsfs`; no filesystem operations except unused RTC helper.
