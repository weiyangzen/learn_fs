# sources/test-tools/ltp/testcases/kernel/syscalls/fanotify/fanotify10.c

Purpose: Large regression matrix for ignore mask logic across inode, parent, mount, filesystem, evictable marks, exec events, bind mounts, priority classes, and legacy versus `FAN_MARK_IGNORE` variants.

Important APIs/types/functions: `FAN_MARK_IGNORED_SURV`, `FAN_MARK_IGNORE_SURV`, `FAN_MARK_EVICTABLE`, `FAN_OPEN`, `FAN_OPEN_EXEC`, `FAN_EVENT_ON_CHILD`, `FAN_ONDIR`, `/proc/*/fdinfo`, cache dropping, bind mounts, and child exec/open generation.

Control flow: Setup creates a directory tree, many optional files/dirs, helper executables, and a bind mount. Each case creates fanotify groups across classes/priorities, applies normal and ignore marks, generates an open or exec event in a child, verifies event counts/masks per group, then cycles mounts.

State and persistence behavior: State is extensive: mounted filesystem, bind mount, ignore marks that may be evicted, per-class event queues, cache pressure sysctl, and child pid identity.

Dependencies and integration points: Requires root, mounted filesystem, forked child helpers, save/restore of `vfs_cache_pressure`, and runtime feature gates for filesystem, evictable, ignore, reported-name, and exec events.

Risks and test signals: This is the highest-flake-risk fanotify file because it depends on cache eviction and many feature combinations. It deliberately skips undefined pre-5.9 ignored-child semantics.
