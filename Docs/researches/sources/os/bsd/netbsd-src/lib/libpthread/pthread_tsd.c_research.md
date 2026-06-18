# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_tsd.c

This file implements pthread key lifecycle and thread-exit destruction for thread-specific data. `pthread_tsd_init` registers atfork handlers, reads `PTHREAD_KEYS_MAX` from the environment with a POSIX minimum clamp, computes per-thread TSD storage size, and uses `mmap` rather than malloc for early initialization. It allocates global per-key lists and destructor arrays in one arena.

`pthread_key_create` searches from `nextkey` for an unused destructor slot, uses an internal no-op destructor when the requested destructor is `NULL`, initializes the key's global list expectation, advances `nextkey`, and returns the key. `pthread__add_specific` records a non-null value in the current thread and inserts the per-thread key entry into the global per-key list the first time it is used. `pthread_key_delete` implements the standard's no-destructor rule by removing all entries for that key, setting values to `NULL`, clearing link state, and freeing the key slot.

`pthread__destroy_tsd` runs exit-time destructors up to `PTHREAD_DESTRUCTOR_ITERATIONS`, clearing values before invocation. `pthread__copy_tsd` migrates libc TSD slots into pthread storage during initialization.

Risks are undefined behavior under concurrent key deletion/use, deliberate unsynchronized fast `pthread_getspecific`, and destructor loops that can reestablish values.
