# File Research: sources/os/linux/linux/fs/compat_binfmt_elf.c

## Purpose
Builds 32-bit compatible ELF executable and core-dump support on 64-bit kernels by macro-specializing the common `binfmt_elf.c` implementation.

## Main Elements
- Defines `ELF_COMPAT` and maps ELF layout types to `elf32_*` types.
- Maps coredump ABI types to compat variants: `compat_long_t`, `compat_siginfo_t`, compat prstatus/prpsinfo, and 32-bit timeval conversion.
- Redirects architecture hooks to compat versions when provided, including arch check, platform string, hwcaps, personality setup, dynamic base, thread start, additional pages, and read-implies-exec behavior.
- Renames local symbols such as `elf_format` and init/exit functions to compat names.
- Includes `binfmt_elf.c` to compile the shared implementation under the compat macro environment.

## Dependencies And Integration
Depends on architecture-provided compat macros from `asm/elf.h` and common ELF core definitions from `linux/elfcore-compat.h`. It avoids duplicating ELF loader logic while producing a separate compat binary-format registration.

## Risk Notes
Correctness depends on architecture headers defining compat hooks consistently. Since it macro-includes `binfmt_elf.c`, subtle macro leakage or missing compat definitions can change loader/core behavior across ABIs.
