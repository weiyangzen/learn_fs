# File Research: sources/os/bsd/freebsd-src/sys/sys/auxv.h

## Purpose
`auxv.h` exposes FreeBSD's ELF auxiliary vector lookup API to userland and kernel-adjacent consumers.

## Main Interfaces
- Includes `sys/types.h` and `machine/elf.h`.
- Declares `int elf_aux_info(int aux, void *buf, int buflen);` inside `__BEGIN_DECLS` / `__END_DECLS`.

## Implementation Notes
The header is intentionally minimal: it provides the type context for ELF auxiliary vector constants and one function for copying a requested auxiliary value into a caller-provided buffer. It is a public ABI surface, so the contents are stable and small.

## Dependencies and Constraints
Consumers must provide a correctly sized output buffer for the selected auxiliary vector entry. The implementation lives outside this header.
