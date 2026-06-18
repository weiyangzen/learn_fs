# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_environment.c

## Purpose

Implements DragonFlyBSD kernel environment variable storage, syscalls, tunable fetching helpers, boot-time static environment sysctl traversal, and conversion from bootloader-provided static environment strings to a dynamic kernel-managed array.

## Key Responsibilities

- Maintains `kern_envp`, the bootloader-provided static environment pointer.
- Converts static environment strings into dynamic kernel storage during boot.
- Implements `sys_kenv()` for userland get/set/unset/dump operations.
- Provides in-kernel `kgetenv`, `ksetenv`, `kunsetenv`, `ktestenv`, `kfreeenv`, and typed fetch helpers.
- Supports tunable initialization wrappers for int, long, ulong, quad, and string tunables.
- Exposes static boot environment via `kern.environment` sysctl node.

## Main State

- `kern_envp`: exported static boot environment.
- `kenv_dynp`: dynamic NULL-terminated array of `name=value` strings.
- `kenv_isdynamic`: indicates dynamic environment availability.
- `kenv_dynlock`: spinlock protecting dynamic environment access.
- `M_KENV`: malloc type for dynamic environment storage.
- `KENV_DYNMAXNUM`: maximum dynamic environment entries, 512.

## Syscall Behavior

`sys_kenv()` handles:

- `KENV_DUMP`:
  - Computes needed bytes for all dynamic environment strings.
  - Optionally copies bounded data into a temporary kernel buffer and then out to userland.
  - Returns 0 if full dump fit, or required size if truncated.

- `KENV_GET`:
  - Copies in the name.
  - Uses `kgetenv()`.
  - Copies out up to the user-supplied length.
  - Returns copied length.

- `KENV_SET` and `KENV_UNSET`:
  - Require `caps_priv_check_self(SYSCAP_NOKENV_WR)`.
  - Set or remove dynamic variables.

## Environment Helpers

- `kenv_getstring_dynamic()` searches the dynamic array under lock and optionally returns the index.
- `kenv_getstring_static()` walks the bootloader string block.
- `kernenv_next()` advances through the static NUL-separated environment block.
- `kgetenv()` returns a dynamic malloc copy once dynamic storage exists; before that, it returns a pointer into static storage.
- `ksetenv()` replaces or appends a `name=value` string, enforcing `KENV_MNAMELEN` and `KENV_MVALLEN`.
- `kunsetenv()` removes an entry and compacts the array.
- `kfreeenv()` frees only dynamic copies.
- `ktestenv()` checks for variable existence.
- `kgetenv_string()`, `kgetenv_int()`, `kgetenv_long()`, `kgetenv_ulong()`, `kgetenv_quad()` parse typed values. `kgetenv_quad()` supports `k/m/g/t` suffixes as powers of 1024.

## Boot and Sysctl Integration

- `sysctl_kenv_boot()` exposes indexed static boot environment strings under `kern.environment`.
- `kenv_init()` allocates `kenv_dynp`, copies static environment entries, initializes the spinlock, and sets `kenv_isdynamic`.
- `SYSINIT(kenv, SI_BOOT1_POST, SI_ORDER_ANY, kenv_init, NULL)` performs dynamic setup early after boot stage 1.
- `tunable_*_init()` wrappers fetch tunable values into registered variables.

## Filesystem/Storage Relevance

Kernel environment and tunables influence storage/VFS boot behavior, such as root device selection, driver tunables, debug flags, and filesystem module configuration. This file is the core source of those boot-time and runtime tunable values.

## Research Notes

- Dynamic environment access is spinlock-protected and copies values out before allocating/freeing outside the lock where needed.
- Static-mode `kgetenv()` returns non-owned static memory; dynamic-mode returns owned memory that must be released with `kfreeenv()`.
- `KENV_DUMP` caps buffer size to the maximum possible dynamic environment payload.
- Set/unset are blocked until the dynamic array exists; early boot code must rely on static lookup.
