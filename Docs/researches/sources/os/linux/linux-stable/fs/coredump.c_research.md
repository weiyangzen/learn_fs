# File Research: sources/os/linux/linux-stable/fs/coredump.c

This file implements Linux core dump orchestration, destination parsing, usermode-helper and socket delivery, VMA selection, dump writing helpers, and coredump sysctls.

Key responsibilities:
- Parses `kernel.core_pattern` into file, pipe, socket, or socket-request coredump destinations.
- Coordinates multithreaded process termination and coredump synchronization.
- Creates destination files, pipes to usermode helpers, or AF_UNIX socket connections.
- Invokes binary-format-specific `core_dump()` callbacks.
- Exports helper functions used by core writers: `dump_emit()`, `dump_skip_to()`, `dump_skip()`, `dump_user_range()`, and `dump_align()`.
- Registers sysctls for core naming, pipe limits, note size limits, VMA sorting, and supported modes.
- Snapshots VMAs and computes dump sizes according to `coredump_filter`/MMF flags.

Important control flow:
- `vfs_coredump()` audits, checks dumpability/binfmt support, prepares credentials, waits for other threads, calls `do_coredump()`, then cleans up.
- `coredump_parse()` expands `%` tokens in `core_pattern`, including pid variants, uid/gid, signal, time, hostname, executable names, core limit, CPU, and pipe pidfd fd number.
- Destination setup:
  - `coredump_file()` validates limits, SUID safety, ownership/mode preservation, regular-file type, and truncation.
  - `coredump_pipe()` spawns a usermode helper with stdin connected to a pipe and optionally installs pidfd fd 3.
  - Socket mode connects to a Unix stream socket, registers pidfs coredump metadata, and optionally negotiates request/ack flags.
- Dump writing:
  - `coredump_write()` snapshots VMAs, calls the binfmt core writer under `file_start_write()`, emits pending skip padding if needed, and frees the snapshot.
  - `dump_emit()` and `dump_skip()` maintain logical dump position and file position while respecting size limits and fatal interruption.
  - `dump_user_range()` walks user pages, writes present pages, and creates sparse holes for missing pages.
- VMA snapshot:
  - `vma_dump_size()` applies special mapping, DONTDUMP, DAX, hugetlb, shared/private, anonymous/file-backed, and ELF-header rules.
  - `dump_vma_snapshot()` takes metadata under mmap write lock, verifies ELF header placeholders after unlocking, sums dump size, and optionally sorts by dump size.

Dependencies:
- Relies on binfmt `core_dump()` implementations, especially ELF.
- Integrates with pidfs, proc connector, audit, fsnotify, sysctl, security/dumpability, usermode helper, AF_UNIX, and MM/VMA internals.

Risks and invariants:
- SUID-safe mode requires pipe, socket, or fully qualified file path and may dump as root fsuid.
- `core_pipe_limit` limits concurrent helper-backed dumps and controls whether the crashing task waits.
- Socket paths must be absolute, under initial mount namespace semantics, not contain `..`, not contain spaces, and fit `UNIX_PATH_MAX`.
- `dump_interrupted()` stops dumping on fatal signal or freezer activity.
- VMA metadata holds file references and must be released by `free_vma_snapshot()`.
