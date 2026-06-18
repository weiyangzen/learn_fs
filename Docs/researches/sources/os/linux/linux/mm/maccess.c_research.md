# File Research: sources/os/linux/linux/mm/maccess.c

Fault-suppressed memory access helpers for copying to/from kernel and user addresses from contexts where normal faults must not be taken.

Key responsibilities:
- Provides nofault kernel reads and writes: `copy_from_kernel_nofault()` and `copy_to_kernel_nofault()`.
- Provides nofault string helpers: `strncpy_from_kernel_nofault()`, `strncpy_from_user_nofault()`, and `strnlen_user_nofault()`.
- Provides nofault user copies: `copy_from_user_nofault()` and `copy_to_user_nofault()`.
- Exposes weak arch/filter hook `copy_from_kernel_nofault_allowed()`.
- Exports `__copy_overflow()` warning helper.

Important behavior:
- Kernel nofault copies disable page faults around repeated `__get_kernel_nofault()` or `__put_kernel_nofault()` operations.
- Copy loops choose `u64`, `u32`, `u16`, then `u8` chunks when alignment allows; inefficient unaligned architectures use source/destination alignment to avoid unsafe wide accesses.
- `copy_from_kernel_nofault()` invokes `kmsan_check_memory()` after reading chunks to avoid leaking uninitialized kernel memory.
- `copy_to_kernel_nofault()` invokes `instrument_write()` after stores.
- Kernel string copy always terminates `dst` with NUL on success or fault, returning copied length including the terminating NUL.
- User nofault read checks `__access_ok()` and `nmi_uaccess_okay()` before using `__copy_from_user_inatomic()`.
- User nofault write checks `access_ok()` before using `__copy_to_user_inatomic()`.
- User string copy uses `strncpy_from_user()` with page faults disabled and adjusts return value so success includes the trailing NUL.
- `strnlen_user_nofault()` simply wraps `strnlen_user()` with page faults disabled.

Dependencies:
- Low-level arch uaccess/nofault primitives: `__get_kernel_nofault`, `__put_kernel_nofault`, inatomic user copy helpers, `access_ok`, and `nmi_uaccess_okay`.
- Pagefault disable/enable machinery.
- KMSAN and instrumentation hooks.
- Exported for kernel subsystems that need best-effort probing without faulting.

Notable risks:
- These helpers suppress faults and report `-EFAULT`/zero-style failures; callers must not treat partial destination contents as complete.
- Kernel nofault reads can be filtered by architectures through `copy_from_kernel_nofault_allowed()`, returning `-ERANGE`.
- `strncpy_from_user_nofault()` may copy partial data before returning `-EFAULT`.
- User nofault helpers still depend on architecture-specific inatomic copy correctness in IRQ/NMI-sensitive contexts.
