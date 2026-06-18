# sources/test-tools/stress-ng/stress-fanotify.c

Purpose: implements `fanotify`, a Linux filesystem notification stressor that marks mounted filesystems/mounts for many fanotify events, generates file activity, reads notification metadata, and exercises invalid fanotify calls.

Important APIs/types/functions: `stress_fanotify_account_t` records event counts. `fan_stress_settings[]` and `init_flags[]` enumerate available fanotify masks and initialization flags. `stress_fanotify_supported()` checks `CAP_SYS_ADMIN` and fanotify availability. `fanotify_event_init_invalid()`, `test_fanotify_mark()`, `fanotify_event_init()`, `fanotify_event_clear()`, `stress_fanotify_read_events()`, and `stress_fanotify()` implement the workload.

Control flow: setup installs SIGCHLD handling, creates a temp directory and two filenames, sync-starts, forks a child, and gathers mount points. The child loops creating, closing, writing, reading, renaming, and unlinking a temp file to generate close, access, modify, and rename events. The parent initializes fanotify instances across mounts/filesystems, tests invalid marks, waits with `select()`, reads event buffers, counts known masks, closes event fds, probes `FIONREAD`, and repeatedly tries supported `fanotify_init()` flags for extra kernel coverage.

State and persistence behavior: state is event counters, static mount path storage, fanotify descriptors, aligned read buffer, and temporary files. Temporary files/directories are removed, child is killed, descriptors are closed, marks are flushed/removed, and mount strings are freed on teardown.

Dependencies and integration points: requires `mntent.h`, `sys/select.h`, `sys/fanotify.h`, fanotify syscalls, and `CAP_SYS_ADMIN`. Integrates with stress-ng mount enumeration, capability, temp-dir, killpid, signal, scheduler, metrics, and filesystem-usage helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS`.

Risks: fanotify is privilege-heavy and kernel-version-sensitive. Marking every mount can consume descriptors/marks and trigger `EMFILE`/`ENOMEM`; event masks and report flags vary widely. Permission-event flags are included when available, but the code mainly counts metadata and closes event fds to avoid leaks.

Test signals: run as non-root and with `CAP_SYS_ADMIN`, check skip reasons, run on systems with multiple mounts, confirm event-rate metrics for opens/closes/accesses/modifies, and verify no lingering fanotify fds, marks, child processes, or temp files.
