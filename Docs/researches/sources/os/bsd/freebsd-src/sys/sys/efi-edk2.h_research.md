# File Research: sources/os/bsd/freebsd-src/sys/sys/efi-edk2.h

## Purpose
Adapts EDK2 type names, calling-convention macros, and processor defines for FreeBSD builds that reuse EDK2-derived headers/code.

## Main Elements
- Defines EDK2 integer, pointer, character, boolean, and void type aliases.
- Defines or suppresses EFI API syntax macros such as `EFIAPI`, `IN`, `OUT`, `CONST`, `OPTIONAL`, and `INTERFACE_DECL`.
- Undefines conflicting `NULL`, `EFI_PAGE_SIZE`, `EFI_PAGE_MASK`, `MAX`, and `MIN`.
- Sets `NO_MSABI_VA_FUNCS` outside standalone loader builds.
- Defines `MDE_CPU_*` based on compiler architecture.
- Defines `MAX_BIT` based on long width.

## Dependencies And Integration
Includes standard integer headers and is used when importing EDK2 headers into FreeBSD kernel/userland/loader contexts.

## Risk Notes
Calling convention handling differs for standalone amd64 loader versus kernel/userland. Include order with `sys/param.h` can matter due to `MAX`/`MIN` collisions.
