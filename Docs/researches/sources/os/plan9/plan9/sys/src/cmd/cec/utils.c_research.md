# File Research: sources/os/plan9/plan9/sys/src/cmd/cec/utils.c

This file provides console raw-mode and hex-dump utilities for `cec`.

Key behavior:
- `rawon()` opens `/dev/consctl` and writes `rawon` unless running as a service.
- `rawoff()` closes the raw-mode fd unless running as a service.
- `dump()` formats packet bytes as hex, 16 bytes per line.

Important details:
- Raw-mode failure is reported but not fatal.
- The dump formatter uses a static line buffer.

Filesystem relevance:
- Indirect/direct Plan 9 device use through `/dev/consctl`.
