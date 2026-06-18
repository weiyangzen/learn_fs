# sources/user-network-fs/samba/source3/lib/smbd_shim.c

## Purpose
This file implements a runtime shim table for library code that may be linked into smbd or non-smbd utilities. smbd can install real callbacks; other binaries get safe dummy behavior or process exit fallbacks.

## Important APIs, Types, And Functions
`set_smbd_shim()` copies a caller-provided `struct smbd_shim` into the file-static `shim`. Wrapper functions include `change_to_root_user()`, `become_authenticated_pipe_user()`, `unbecome_authenticated_pipe_user()`, `contend_level2_oplocks_begin()`, `contend_level2_oplocks_end()`, `become_root()`, `unbecome_root()`, `exit_server()`, and `exit_server_cleanly()`.

## Control Flow
Each wrapper checks whether the corresponding function pointer is non-NULL. Boolean wrappers return false when unset. Oplock and privilege wrappers no-op when unset. Exit wrappers call the installed callback if present and otherwise call `exit(1)` or `exit(0)`.

## State And Persistence
State is a single process-global `struct smbd_shim`. There is no persistence. Installing a shim changes behavior process-wide and is not synchronized.

## Dependencies And Integration Points
It depends on `smbd_shim.h` and Samba auth/files types. It breaks dependency cycles by letting common library code refer to smbd-specific privilege, authenticated pipe user, oplock contention, and exit behavior without linking all smbd internals into utilities.

## Risks And Test Signals
Risks include process-global mutable callbacks, no thread-safety during installation, dummy false/no-op behavior hiding missing setup, and exit callback contracts marked noreturn but not enforced after callback return. Tests should verify default behavior in utility builds, installed callback dispatch, exit fallbacks, and shim installation before worker threads.
