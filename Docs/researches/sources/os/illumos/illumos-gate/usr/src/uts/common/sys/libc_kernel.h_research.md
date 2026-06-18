# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/libc_kernel.h

## Role

Consolidation-private libc/kernel contract header. It documents interfaces that are not stable for applications and should only be shared between libc and the kernel.

## Structure

The file contains only the C linkage wrapper and `_EVAPORATE` definition. `_EVAPORATE` is an `_exit()` status used by a `vfork()` child in libc `posix_spawn()` paths so the child disappears without normal SIGCHLD-visible exit semantics when no `execve()` has occurred.

## Dependencies And Consumers

No included headers. The relevant consumer is libc process-spawn implementation and kernel exit handling that recognizes the special status.

## Important Details

The comment explicitly warns that these definitions may change even in a patch. Applications should not include or depend on this header.

## Research Notes

Read completely: 53 lines, 1696 bytes.
