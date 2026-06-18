# sources/test-tools/stress-ng/stress-fcntl.c

Purpose: implements `fcntl`, a broad file-control stressor that exercises descriptor duplication, fd flags, file status flags, owner/signal settings, leases, POSIX and OFD locks, write-life hints, path fds, and platform-specific `fcntl()` commands.

Important APIs/types/functions: `check_return()` filters acceptable `fcntl()` errors. `setfl_flag_perms` stores permutations of supported `F_SETFL` flags. `do_fcntl()` performs all command probes against a regular temp file, bad fd, and optional `O_PATH` fd. `stress_fcntl()` manages shared temp-file creation and the main loop.

Control flow: the stressor builds all flag permutations, creates a temp directory shared by workers with the same parent PID, opens a temp file with retry handling, optionally opens `/bin/true` as an `O_PATH` fd, and sync-starts. Each loop duplicates fds, toggles close-on-exec and append-like flags, sets/get owners and signals, queries leases and owner UIDs, truncates the file for lock tests, applies POSIX locks with `SEEK_SET/CUR/END`, applies open-file-description locks, cycles write-life hints, tests invalid structs/flags/fds, runs path-fd commands, then increments bogo operations.

State and persistence behavior: persistent state is limited to a temporary file/directory that are unlinked/removed at teardown. Runtime state includes fd flag permutations and lock ranges. Some file flags, owners, signals, locks, and hints are changed on the open temp fd but discarded when it closes.

Dependencies and integration points: depends on whichever `F_*` constants the platform provides; unavailable commands compile out. Uses stress-ng temp-file, bad-fd, racy-unused-pid, syscall, random, and process-state helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS` with always-on verification.

Risks: `fcntl()` semantics are highly OS and filesystem dependent. Some expected failures are `EINVAL`, `EINTR`, `EPERM`, `EAGAIN`, `EACCES`, or `EDEADLK`; incorrect filtering can create false failures. Shared temp directories mean one worker may see `ENOENT` when another has already removed the directory, which the code treats as successful shutdown.

Test signals: run multiple workers with `--verify`, on Linux and BSD-like builds, confirm no unexpected `fcntl` failures, no stale temp directory, lock operations do not deadlock, and new kernel commands such as `F_DUPFD_QUERY`/`F_CREATED_QUERY` return expected boolean-like results when available.
