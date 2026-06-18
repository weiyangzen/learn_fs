# File Research: sources/local-fs/dlm/python/bindings/dlm.py

## Purpose
Python ctypes wrapper around `libdlm_lt`.

## Behavior
- Exits on non-Linux platforms.
- Locates `dlm_lt` with `ctypes.util.find_library`.
- Loads the library with `ctypes.CDLL`.
- Defines ctypes representations for lockspace handles and `struct dlm_lksb`.
- Binds `dlm_create_lockspace`, `dlm_release_lockspace`, `dlm_ls_lock_wait`, and `dlm_ls_unlock_wait`.
- Defines Python enums for lock modes, lock flags, and lock status block flags.
- Provides `Lockspace` class and nested per-resource `Lock` objects.

## API Model
- `Lockspace(name="default", mode=0o600)` creates a kernel DLM lockspace.
- `release(force=2)` releases it.
- `create_lock(name)` returns a lock object.
- `Lock.lock_wait()` synchronously locks; default mode is exclusive.
- `Lock.unlock_wait()` synchronously unlocks.
- Destructors attempt cleanup of held locks and lockspaces.

## Risks / Gaps
- Constructor maps a null handle to `ENOMEM`, losing the real C `errno`.
- Callback objects for BAST are local variables; if the C layer retains them beyond the synchronous call, lifetime may be unsafe.
- `C_DLM_LKSB.sb_flags` is `ctypes.c_char`; `LockSBFlag(flags[0])` depends on bytes indexing semantics.
- Destructor cleanup can raise through `release()`/`unlock_wait()` during garbage collection.
