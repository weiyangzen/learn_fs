# File Research: sources/os/bsd/freebsd-src/sys/sys/types.h

Foundational FreeBSD typedef and small compatibility utility header.

Key responsibilities:
- Includes compiler definitions, machine endian definitions, base private types, offset definitions, and pthread types.
- Defines BSD/System V compatibility integer aliases, deprecated `u_int*_t` and quad types, address pointer aliases, core POSIX scalar types, capability types, kernel-export-safe address/size types, VM scalar types, resource types, and syscall argument type.
- Under kernel/standalone builds, defines kernel-only types such as `boolean_t`, `device_t`, interrupt mask, user offset, memory attribute, and `vm_page_t`, plus C bool shims for older C modes.
- Under BSD visibility, includes select definitions, defines `major`, `minor`, and `makedev` encoders/decoders for FreeBSD `dev_t`, and provides enum-width helper macros for uint8-backed enums.
- Declares legacy-visible `ftruncate`, `lseek`, `mmap`, and `truncate` prototypes for non-kernel compatibility.

Dependencies:
- Central header depending on many low-level machine and sys private type headers.

Notable risks:
- This header is transitively included almost everywhere; namespace pollution is intentional but any change has very wide blast radius.
- `dev_t` encoding/decoding preserves historical compatibility and should not be casually changed.
