# File Research: sources/os/bsd/freebsd-src/sys/kern/systrace_args.c

## Purpose

`systrace_args.c` is an automatically generated DTrace syscall-provider helper. It does not implement syscall behavior. It translates FreeBSD syscall argument structs and syscall metadata into uniform DTrace-visible argument arrays and textual type descriptions.

The file explicitly says it is generated and should not be edited by hand.

## Structure

The file contains three static functions:

- `systrace_args(int sysnum, void *params, uint64_t *uarg, int *n_args)`
- `systrace_entry_setargdesc(int sysnum, int ndx, char *desc, size_t descsz)`
- `systrace_return_setargdesc(int sysnum, int ndx, char *desc, size_t descsz)`

Each function is a large `switch (sysnum)` table covering the same 422 syscall case labels, from syscall number `0` through the highest listed syscall `602` (`renameat2`). Sparse syscall numbers are intentionally omitted or grouped according to the generated syscall table.

## `systrace_args()`

`systrace_args()` converts a syscall-specific argument struct into a DTrace register-style argument vector:

- Casts `uarg` to both unsigned and signed views:
  - `uint64_t *uarg`
  - `int64_t *iarg = (int64_t *)uarg`
- Uses an incrementing index `a`.
- For each syscall with arguments:
  - Casts `params` to `struct <syscall>_args *`.
  - Copies integer-like signed values into `iarg[a++]`.
  - Copies unsigned sizes, flags, and pointer addresses into `uarg[a++]`.
  - Casts user pointers through `(intptr_t)` before storing.
  - Sets `*n_args` to the number of copied arguments.
- For syscalls without arguments, sets `*n_args = 0`.
- The `default` case also sets `*n_args = 0`.

The largest argument counts in the table are seven arguments, including `sendfile`, `afs3_syscall`, and several SCTP generic send/receive syscalls. Six-argument examples include `recvfrom`, `sendto`, `mmap`, `__sysctl`, `kevent`, `copy_file_range`, and `wait6`.

## `systrace_entry_setargdesc()`

`systrace_entry_setargdesc()` maps `(sysnum, argument_index)` to a human-readable entry argument type string. It mirrors the syscall argument table used by `systrace_args()`.

Important behavior:

- Initializes `const char *p = NULL`.
- Switches on syscall number.
- For each syscall with arguments, switches on `ndx`.
- Assigns strings such as:
  - `int`
  - `size_t`
  - `off_t`
  - `uid_t`
  - `userland const char *`
  - `userland void *`
  - `userland struct stat *`
  - `userland const struct timespec *`
- Copies the string with `strlcpy(desc, p, descsz)` only when `p != NULL`.
- Unknown syscall numbers or out-of-range indexes leave `desc` unchanged.

The generated descriptions preserve an important distinction between scalar kernel-visible values and userland pointers, which is useful for DTrace consumers and probe argument display.

## `systrace_return_setargdesc()`

`systrace_return_setargdesc()` maps syscall number and return-value index to return type descriptions.

Behavior:

- Uses `p = NULL` and a syscall-number switch.
- Most syscalls describe return indexes `0` and `1` identically.
- Common return descriptions include:
  - `int`
  - `ssize_t`
  - `void`
  - `void *`
  - `off_t`
  - `mode_t`
- Examples:
  - read/write style syscalls return `ssize_t`.
  - descriptor-creating syscalls commonly return `int`.
  - `mmap` and `shmat` return `void *`.
  - `_exit`, `thr_exit`, and `abort2` are described as `void`.
- Unknown syscalls or unsupported indexes leave `desc` unchanged.

## Dependencies and Integration

This file assumes the generated syscall argument structs, syscall numbers, and helper prototypes are available from the surrounding compilation unit or generated include context. It uses standard kernel string copying via `strlcpy()` but has no includes of its own in this generated body.

It is coupled tightly to the FreeBSD syscall table. Any syscall ABI change requires regeneration, not manual editing.

## Research Notes

This is metadata plumbing for observability. The main maintenance risk is stale generated output: mismatches between syscall numbers, `struct <name>_args` layout, and DTrace descriptions would cause incorrect tracing metadata rather than syscall execution bugs. Because all three generated switches must stay synchronized, regeneration from the canonical syscall definitions is the right update path.
