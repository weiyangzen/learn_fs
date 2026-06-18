<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/pathtrace.c -->
# sources/test-tools/strace/src/pathtrace.c

Purpose: implements path and fd matching for strace path filtering.

Important APIs/types/functions: `global_path_set`, `pathtrace_select_set`, `pathtrace_match_set`, `get_proc_pid_fd_path`, `getfdpath_pid`, `pathmatch`, `upathmatch`, `fdmatch`, `match_xselect_args`, and `storepath`.

Control flow: selected paths are stored literally and with realpath canonicalization. Matching dispatches by syscall semantic number (`sen`) to inspect the correct path and fd arguments for file, descriptor, network, mmap, poll/select, fanotify, mount, link/rename, and fsconfig cases; otherwise it falls back to arg0 based on syscall trace flags.

State and persistence behavior: `global_path_set` and caller-provided `path_set` arrays persist selected paths. It reads `/proc/<pid>/fd` links and detects `" (deleted)"` suffixes by comparing link and path stat data.

Dependencies and integration points: used by trace filtering; depends on syscall metadata flags, number sets, proc pid translation, largefile stat wrappers, fd/path printers, and quiet option state.

Risks: syscall-specific argument knowledge must stay synchronized with syscall decoders. `/proc` path resolution can fail under namespaces or permissions. Large fd sets are capped to limit work.

Test signals: path filters for openat/linkat/renameat/mmap/poll/select/fanotify/fsconfig, fd-set filters, deleted fd symlinks, canonical path logging, and fallback behavior for new trace-flagged syscalls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/pathtrace.c -->
