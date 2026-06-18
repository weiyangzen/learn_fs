# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/fail.c

Implementation of Antiword’s assertion-like failure path.

Important behavior:
- Compiled only when `NDEBUG` is not defined.
- `__fail()` validates its inputs, optionally logs debug details to stderr under `DEBUG`, then calls `werr(1, ...)` with expression, filename, and line number.
- Intended to terminate through Antiword’s error handler.

Role:
- Central runtime guard for `fail()` checks in debug/assert-enabled builds.
