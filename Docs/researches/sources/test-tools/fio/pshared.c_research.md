# sources/test-tools/fio/pshared.c

Purpose: initializes pthread mutexes and condition variables with optional process-shared and monotonic-clock attributes.

Important APIs/functions: `cond_init_pshared()`, `mutex_init_pshared_with_type()`, `mutex_init_pshared()`, and `mutex_cond_init_pshared()`.

Control flow: each initializer creates the relevant pthread attribute object, conditionally sets `PTHREAD_PROCESS_SHARED` under `CONFIG_PSHARED`, conditionally sets condition-variable clock to `CLOCK_MONOTONIC`, initializes the synchronization object, logs errors, and returns pthread error codes. Mutex attributes are destroyed after successful mutex initialization.

State and persistence: no global state; initializes caller-owned pthread objects.

Dependencies and integration: pthreads, fio logging, and platform configure macros. Used where synchronization objects may live in shared memory or need monotonic timeouts.

Risks: error paths in `cond_init_pshared()` do not destroy initialized condition attributes before returning. If mutex initialization succeeds but condition initialization fails in `mutex_cond_init_pshared()`, the mutex remains initialized and caller must clean up.

Test signals: platforms with and without `CONFIG_PSHARED`, monotonic condattr support, each mutex type, and failure injection for attr/init calls.
