# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_kcov.c

Read completely: 805 lines.

Implements NetBSD's KCOV coverage device and sanitizer coverage hooks. Opening `/dev/kcov` clones a file descriptor backed by `kcov_fileops`; ioctls allocate buffers, enable/disable tracing, and attach/detach remote coverage buffers.

Core behavior:
- `kcov_allocbuf()` creates an anonymous UVM object, maps it wired into the kernel, and exposes it to userland via `fo_mmap`.
- Normal descriptors are owned by one enabled LWP through `l->l_kcov`.
- Remote coverage records are registered by subsystem/id and use preallocated maximum-size buffers.
- Remote enter/leave temporarily assigns a remote descriptor to the current LWP if enabled.
- Trace PC mode records return addresses; trace CMP mode records comparison metadata and operands.
- `kcov_silence_enter()`/`leave()` suppress tracing around sensitive instrumentation paths such as lockdebug.

Risks and notes:
- Tracing is skipped during cold boot and interrupt context.
- Descriptor close defers freeing if the descriptor is still active on an LWP.
- Remote registration assumes one active reference at a time and panics on duplicate registration or missing remote IDs.
- Instrumentation functions must avoid external calls and are marked `__nomsan`.
