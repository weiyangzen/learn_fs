# File Research: sources/os/bsd/netbsd-src/sys/sys/spawn.h

Read completely: 109 lines.

This header defines NetBSD's internal POSIX spawn attribute and file-action layouts. `struct posix_spawnattr` stores flags, process group, scheduling parameter/policy, default signal set, and signal mask. File actions support open, dup2, close, chdir, and fchdir entries through `posix_spawn_file_actions_entry_t`.

It defines POSIX spawn flags for reset IDs, set process group, set scheduling parameters/policy, set signal defaults, and set signal mask. NetBSD adds `POSIX_SPAWN_RETURNERROR`, which forces parent-side waiting for child setup errors, mainly for testing.

Risks: action entries contain owned path pointers. The return-error extension changes synchronization/error-reporting behavior and should not be assumed by portable callers.
