# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_fslog.c

## Scope

This file contains the VFS filesystem logging hook for external process modification message tracing.

## Public And Internal APIs Covered

- Defines `fslog_extmod_msgtracer(proc_t caller, proc_t target)`.

## Control Flow And Behavior

The implementation is currently compiled out with `#if 0` due to the referenced radar. The disabled body would format caller and target process names plus executable UUIDs, escape them, optionally print debug output, and emit a MessageTracer ASL kernel log message for external modification.

## State And Data Structures

No active runtime state is maintained. The disabled code uses stack buffers sized for process names plus UUID strings.

## Dependencies

Includes process, vnode, mount, syslog, UUID, allocation, and historical ASL/KASL headers, though the active function is effectively a no-op.

## Risks And Invariants

- Because the functional body is disabled, callers receive no logging side effect.
- If re-enabled, process locking assumptions in the comment matter: caller and target are expected to be appropriately locked.
- Escaping failures intentionally abort logging in the disabled implementation.
