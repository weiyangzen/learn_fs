# File Research: sources/os/linux/linux/io_uring/futex.h

## Purpose
Declares io_uring futex opcode handlers, cancellation hooks, and config-dependent stubs.

## Main Contents
- Prototypes for futex prep, wait, waitv, and wake.
- Under `CONFIG_FUTEX`, prototypes for cancel/remove-all and cache init/free.
- Without futex support, cancel returns neutral values, remove-all returns false, cache init returns false, and cache free is a no-op.

## Cross-File Relationships
- Implemented by `futex.c`.
- Included by cancellation and opcode dispatch paths.

## Risks / Review Notes
- Disabled-config stubs intentionally make futex cancellation/cache hooks safe to call unconditionally.
