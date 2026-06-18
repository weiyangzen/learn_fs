# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/bitext.h

This small header declares typed helper functions for extracting, setting, and deleting bit ranges from integer values. It is intended as a safer replacement for the `BITX` macro family with better error handling.

Key contents:
- Extraction functions:
  - `bitx8`, `bitx16`, `bitx32`, `bitx64`
- Bit range set functions:
  - `bitset8`, `bitset16`, `bitset32`, `bitset64`
- Delete helper:
  - `bitdel64`

Dependencies:
- Includes `sys/types.h`.
- C++ guarded with `extern "C"`.

Research notes:
- The header only declares functions; behavior and error handling live in implementation/manpage references such as `bitx64(9F)`, `bitdel64(9F)`, and `bitset64(9F)`.
