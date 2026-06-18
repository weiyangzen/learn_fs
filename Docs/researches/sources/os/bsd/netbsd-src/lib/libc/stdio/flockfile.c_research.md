# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/flockfile.c

Read completely: 183 lines.

This file implements `flockfile`, `ftrylockfile`, `funlockfile`, and internal lock/unlock helpers. In reentrant builds it tracks recursive ownership, waits on a condition variable, and disables cancellation around internal locks; non-reentrant builds are no-ops.

Important interactions: all stdio functions use the locking state defined in `fileext.h`.

Security/reliability notes: assumes `thr_t` behaves as a pointer-like value. Internal lock cancellation-state handling is delicate because condition waits are cancellation points.
