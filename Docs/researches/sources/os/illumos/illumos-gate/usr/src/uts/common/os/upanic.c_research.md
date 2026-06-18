# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/upanic.c

Implements `upanic()`, a user-process abort path intended to force a core dump with a small user-supplied panic message stored in procfs/core metadata.

Key responsibilities:
- Marks the current LWP as taking `SIGABRT`.
- Stops other LWPs with `proc_is_exiting()` and `exitlwps()`.
- Copies up to `PRUPANIC_BUFLEN` bytes of user message data into kernel memory.
- Sets `p_upanic` and `p_upanicflag` bits describing message presence, truncation, invalid copyin, and panic state.
- Coordinates audit events around the core dump when auditing is enabled.
- Calls `core(SIGABRT, B_FALSE)` and exits as `CLD_DUMPED` or `CLD_KILLED`.

Important details:
- The message buffer is zero-filled and truncated at the fixed procfs upanic buffer length.
- Copyin failure clears the have-message flag and records invalid-message state.
- `p_lock` protects current signal and process upanic fields.

Filesystem relevance:
- This is process/core-dump plumbing. It intersects filesystem behavior through `core()`, which writes a core file using the normal kernel core dump and vnode/filesystem path, and through procfs exposure of upanic state.
