# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/core.c

This file implements core dump orchestration: selecting per-process/per-zone/global core destinations, safely creating files, expanding core filename patterns, temporarily adjusting credentials for privileged dump locations, invoking executable-format core writers, and writing process memory segments.

Core behavior:
- Core destinations are classified as `CORE_PROC`, `CORE_ZONE`, or `CORE_GLOBAL`.
- `core_log()` emits zone-scoped syslog messages for global/zone core dumps when `CC_GLOBAL_LOG` is enabled.
- `remove_core_file()` is a private unlink path that can operate relative to the process root, zone root, or global root; it refuses directories, read-only filesystems, unwritable files, and files with conflicting NBMAND share reservations.
- `create_core_file()` creates a new core with `FWRITE | FTRUNC | FEXCL | FCREAT | FOFFMAX`, using special lookup for zone/global locations that may be inaccessible under chroot or zone path limits.
- Created core files must be owned by the dumping credential’s uid; otherwise they are closed, removed, and rejected.
- `set_cred()` swaps a held credential into the process, updates per-user process counts if real uid changes, calls `crset()` for all threads, and returns a held old credential.
- `do_core()` determines applicable content and rlimit, rejects zero rlimit, enforces set-id/SNOCD core policy, temporarily switches to zone `kcred` for global/zone or set-id dumps, removes any existing target, creates the new target with exclusive create, restores original process credentials, and calls the executable format’s `exec_core()` method.
- Existing core files are removed before exclusive creation to avoid symlink/hardlink attacks, dumping into a mapped old core file, and concurrent clobbering.
- `expand_string()` expands core path tokens such as `%p`, `%u`, `%g`, `%f`, `%d`, `%n`, `%m`, `%t`, `%z`, `%Z`, and `%%`, with length checks and special `%d` pathname lookup.
- `dump_one_core()` expands a zone/global core pattern, calls `do_core()`, logs success and common failure cases, invokes core rctl actions on `EFBIG`, and optionally returns the allocated path string.
- `core()` is the main entry point. It checks whether any core paths are enabled, blocks most signals while preserving termination signals, marks `SDOCORE`, frees watched pages, moves current signal info aside, dumps per-process, per-zone, and global-zone cores as configured, restores the signal mask, and notifies process contracts via `contract_process_core()`.
- `core_seg()` writes a process memory range in chunks, skipping holes/non-memory via `as_memory()`, capping each write to `core_chunk * PAGESIZE`, and aborting on real signals.
- `core_write()` wraps `vn_rdwr()` so callers get complete-write-or-errno behavior, retrying partial writes and returning `ENOSPC` if no progress is made.

Important invariants:
- Core dumping may temporarily use zone `kcred` for filesystem access but restores process credentials before `exec_core()` records process credential information.
- Set-id or `SNOCD` processes dump only when global/process set-id core options allow it.
- Zone/global core paths deliberately bypass ordinary chroot/zone path restrictions using selected root/start vnodes.
- `core()` clears the current signal while doing file I/O because pending signal state can interfere with network filesystem writes.
- Offset arithmetic in `core_seg()` and `core_write()` is checked against `OFF_MAX` and wraparound.
- `core_write()` treats zero-progress successful `vn_rdwr()` as `ENOSPC`.
