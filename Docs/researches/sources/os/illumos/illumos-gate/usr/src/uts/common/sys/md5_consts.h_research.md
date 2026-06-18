# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/md5_consts.h

Purpose: Defines the MD5 round constants, initialization constants, and shift amounts from RFC 1321.

Key definitions:
- `MD5_CONST_0` through `MD5_CONST_63`.
- Initial state constants `MD5_INIT_CONST_1` through `MD5_INIT_CONST_4`.
- Shift constants for all four MD5 rounds.

Important detail: This header contains constants only; the transform logic is elsewhere.

Relevance to subset A: General digest implementation support.
