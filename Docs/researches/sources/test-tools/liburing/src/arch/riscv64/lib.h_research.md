# sources/test-tools/liburing/src/arch/riscv64/lib.h

## sources/test-tools/liburing/src/arch/riscv64/lib.h

Purpose: RISC-V 64 page-size helper with libc and nolibc paths.

Important APIs/functions: `__get_page_size` and cached `get_page_size`, equivalent in behavior to the AArch64 helper.

Control flow: libc mode uses `sysconf`; nolibc mode reads `/proc/self/auxv` looking for `AT_PAGESZ`; public helper caches result.

State and persistence: static page-size cache; procfs read in nolibc.

Dependencies/integration: included by RISC-V liburing internals; depends on raw syscall wrappers for nolibc.

Risks: includes `<sys/auxv.h>` even though nolibc path manually reads auxv; availability depends on headers. Fallback to 4096 may be wrong on systems with different page size.

Test signals: riscv64 CI compile and any nolibc runtime mapping tests.
