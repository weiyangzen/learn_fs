# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/audit_core.c

This file initializes and manages core per-process, per-thread, and per-file audit data used by the C2 audit subsystem. It also handles audit context updates after policy changes and provides fork/exit/thread/file allocation hooks.

`audit_init()` checks whether the `c2audit` module is explicitly excluded. If excluded, auditing is permanently disabled; otherwise it marks audit unloaded-loadable, initializes the process audit data cache, initializes per-zone audit contexts, allocates initial thread and process audit data for `curthread` and `curproc`, patches existing kernel threads to use the initial thread audit data, initializes `kcred` audit info with `AU_NOAUDITID`, and creates initial root/current-directory audit paths.

`audit_update_context()` applies pending per-process audit mask updates. If `PAD_SETMASK` is set, it obtains or uses a preallocated credential, locks the process audit data, copies the current credential to the new one under `p_crlock`, updates the audit mask, clears the pending flag, and either installs it for `curproc` with `crset()` or frees the extra reference for other processes.

`audit_newproc()` allocates child process audit data during fork, copies the parent’s audit path/data under the parent pad lock, holds root and cwd paths, and, when full auditing is active, completes the parent fork audit record before the child runs. `audit_pfree()` releases audit paths and frees per-process audit data on exit or fork failure, except for the immortal initial `pad0`.

Thread and file hooks are straightforward. `audit_thread_create()` allocates zeroed `t_audit_data` for new threads. `audit_thread_free()` skips the initial shared `tad0`, asserts no residual audit record/path state, releases deferred at-path state, frees deferred records if auditing is loaded, and frees the thread audit data. `audit_falloc()` attaches `f_audit_data` to new file structures, and `audit_unfalloc()` releases saved audit paths and frees file audit data. `audit_getstate()` reports whether auditing is loaded and enabled for the current thread.

Important dependencies include audit caches from `audit_memory.c`, zone setup from `audit_zone.c`, credentials, process/thread/file lifecycle hooks, audit record/token helpers, and path reference management. Risks are primarily lifecycle and locking: audit path references must be held/released correctly across fork and exit, credential replacement must use the right locks, and initial kernel threads share bootstrap audit data.
