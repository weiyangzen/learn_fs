# sources/user-network-fs/samba/source3/modules/vfs_preopen.c

## Purpose
`vfs_preopen.c` improves sequential numbered-file access by forking helper processes that open and read the first bytes of likely upcoming files. It is a cache-warming module driven by filename patterns and numeric sequences.

## Important APIs, Types, And Functions
- `struct preopen_state` stores helper pool, queue limits, logging levels, matching state, filename template, digit position/count, and queued numeric range.
- `struct preopen_helper` tracks child pid, socket fd, tevent fd, and busy status.
- Helper lifecycle: `preopen_init_helper`, `preopen_helper`, `preopen_helper_open_one`, `preopen_helper_readable`, `preopen_helper_destroy`, and `preopen_helpers_destructor`.
- Queue logic: `preopen_queue_run`, `preopen_parse_fname`, `num_digits_max_value`.
- `preopen_state_get()` lazily initializes state from `preopen:*` parameters and creates wildcard or POSIX basic regex matchers.
- `preopen_openat()` is the only VFS hook.

## Control Flow
On each open, the module lazily creates helpers if `preopen:names` is configured, delegates the real open first, then only continues for successful read-only file opens. It requires an absolute directory path and relative non-dot basename. The basename is matched against configured patterns. If matched, the module constructs an absolute template, discovers a numeric field, detects sequence resets when the pattern, digit offset, digit count, prefix, or suffix changes, advances sent counters, computes a bounded queue end, and pushes future filenames over idle helper sockets. Helpers read a NUL-terminated pathname, open it read-only, read `num_bytes`, and signal completion with one byte.

## State And Persistence
Per-handle state persists for the VFS handle lifetime and owns child processes. Child helpers are killed and waited in the destructor. No on-disk state is changed; effects are kernel page-cache warming only.

## Dependencies And Integration Points
It depends on `tevent`, socketpairs, fork, `sys_rw`, Samba path matching helpers, global event context, and VFS open hooks. Configuration includes `preopen:names`, `preopen:num_bytes`, `preopen:helpers`, `preopen:queuelen`, `preopen:posix-basic-regex`, and log-level knobs.

## Risks
- Forked helper management must avoid leaking children or descriptors; destructor correctness is important.
- Helpers use raw POSIX `open()` on constructed absolute paths, bypassing parts of Samba VFS policy for the speculative read path.
- Numeric parsing assumes useful sequences have at least three adjacent digits unless regex replacement hints provide exact positions.
- Aggressive queues can create extra backend I/O for users who skip around in a sequence.

## Test Signals
- Configure wildcard and regex `preopen:names`; open `file001` and observe helper opens for subsequent numbers.
- Verify reset behavior when moving to a different pattern, digit width, prefix, or suffix.
- Confirm write opens, relative directories, dot names, and absolute basenames bypass preopen.
- Run under process/fd leak checks and verify helpers terminate when the VFS handle is destroyed.
