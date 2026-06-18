# sources/test-tools/strace/src/kernel_fcntl.h

Purpose: sanitizes userspace fcntl macro/type namespace before including kernel `<asm/fcntl.h>`.

Important APIs/types/functions: temporary renames `f_owner_ex`, `flock`, `flock64`, many `O_*`/`F_*`/`LOCK_*` undefines, inclusion of `<asm/fcntl.h>`, and final `#undef O_NDELAY`.

Control flow: if `_ASM_GENERIC_FCNTL_H` is not already included, the header undefines potentially conflicting libc/generic constants, renames structure tags to kernel-prefixed forms, includes the architecture kernel fcntl header, then removes temporary tag aliases. It always undefines `O_NDELAY` afterward so strace can correct architecture-specific definitions elsewhere.

State and persistence behavior: no runtime state; it mutates preprocessor namespace for later decoder includes.

Dependencies and integration points: used by fcntl/open flag decoders needing kernel ABI constants instead of libc values. It depends on configure/build include ordering and architecture headers.

Risks: the list of undefines must track kernel `asm-generic/fcntl.h`; missing a macro can cause redefinition warnings or wrong constants. The `O_NDELAY` correction is architecture-sensitive, especially sparc32.

Test signals: build across multiple architectures, validate open/fcntl flag numeric values, and specifically check `O_NDELAY` rendering on sparc-like and generic platforms.
