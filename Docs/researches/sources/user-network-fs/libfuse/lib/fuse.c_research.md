# sources/user-network-fs/libfuse/lib/fuse.c

## Purpose

`fuse.c` implements libfuse's high-level path-based API on top of the low-level `fuse_session` request API. It translates kernel-facing inode/nodeid requests into user filesystem paths, invokes callbacks from `struct fuse_operations`, manages the high-level `struct fuse` lifecycle, and owns high-level conveniences such as hidden-file deletion, readdir buffering, node remembering, module stacking, interrupt delivery, and option parsing.

The file is the main bridge between applications using `fuse_new()`, `fuse_loop()`, `fuse_mount()`, and path-oriented callbacks such as `getattr`, `read`, `write`, `readdir`, `rename`, and `unlink`, and the lower-level dispatcher that works with `fuse_req_t`, `fuse_lowlevel_ops`, and kernel protocol opcodes.

## Important APIs, Types, And Functions

Core private types include `struct fuse_fs`, which wraps `struct fuse_operations`, user data, and debug state; `struct fuse`, which owns the `fuse_session`, node tables, LRU list, config, lock, module stack, and cleanup thread; `struct node`, which maps libfuse node ids to parent/name/path state and open/cache/lock metadata; `struct node_table`, which is a split-growing hash table used for both id and name indexes; `struct fuse_dh`, which tracks high-level directory handles and buffered directory entries; and `struct fuse_context_i`, which extends public `struct fuse_context` with the current request.

The public and ABI-versioned entry points include `fuse_fs_new`, `_fuse_new_31`, `_fuse_new_30`, `fuse_new_31`, `fuse_new_30`, `fuse_destroy`, `fuse_mount`, `fuse_unmount`, `fuse_get_session`, `fuse_loop`, `fuse_loop_mt_312`, `fuse_loop_mt_32`, `fuse_loop_mt_31`, `fuse_exit`, `fuse_get_context`, `fuse_getgroups`, `fuse_interrupted`, `fuse_invalidate_path`, `fuse_clean_cache`, `fuse_notify_poll`, `fuse_version`, and `fuse_pkgversion`.

The callback wrapper layer is exposed inside libfuse as `fuse_fs_*` helpers such as `fuse_fs_getattr`, `fuse_fs_open`, `fuse_fs_read_buf`, `fuse_fs_write_buf`, `fuse_fs_readdir`, `fuse_fs_lock`, `fuse_fs_statx`, and `fuse_fs_syncfs`. These wrappers set `fuse_get_context()->private_data`, apply debug logging, provide fallback behavior where appropriate, and normalize absent callbacks to `-ENOSYS` or success depending on operation semantics.

`fuse_path_ops` is the low-level operation table. Its handlers, named `fuse_lib_*`, receive nodeids and request objects, reconstruct or lock paths, call the `fuse_fs_*` wrapper, update high-level caches, and send low-level replies.

## Control Flow

Construction starts in `_fuse_new_31`: allocate `struct fuse`, initialize default timeouts and interrupt signal, parse `fuse_lib_opts`, register built-in modules, create the thread-local context key, build a base `fuse_fs`, optionally push `modules=` layers, create a versioned `fuse_session` with `fuse_path_ops`, initialize name/id hash tables, initialize locks and LRU/slab lists, create the root node, and return the high-level handle. The 3.0 compatibility constructors add `--help` handling before delegating.

Request processing flows from a loop (`fuse_loop`, `fuse_loop_mt_*`, or lower-level session loop) into `fuse_session_process_buf_internal`, which dispatches through `fuse_path_ops`. Each handler calls `req_fuse_prepare` to create a thread-local context populated with uid, gid, pid, and umask from `fuse_req_ctx(req)`. The handler then obtains a path with `get_path`, `get_path_name`, `get_path_wrlock`, or `get_path2`; prepares interrupt handling if enabled; calls the corresponding high-level operation wrapper; updates node or directory-handle state; and replies with `fuse_reply_*` or `reply_err`.

Path reconstruction walks from a node to the root through parent pointers under `f->lock`, prepending names into a dynamically resized path buffer. Mutating operations can take tree locks on destination nodes or ancestor paths. If a conflicting tree lock exists, `lock_queue_element` instances are queued on `f->lockq` and signaled by `wake_up_queued` when paths are unlocked.

Lookup and cache flow is split between `lookup_path`, `do_lookup`, and `find_node`. A successful filesystem `getattr` creates or finds a `node`, assigns a generation and nodeid, inserts it into name/id hash tables, increments lookup counts, sets entry and attribute timeouts, and optionally records stat data for `auto_cache`. `FORGET` and `FORGET_MULTI` decrease `nlookup`; remembered nodes can be moved to an LRU list instead of being immediately freed.

File open/create paths call the filesystem callback, set policy flags such as `direct_io`, `keep_cache`, `parallel_direct_writes`, and `noflush`, increment `open_count`, and reply with open/create data. Release decrements `open_count` and removes `.fuse_hidden*` files when the last handle closes. Reads and writes use buffer-vector helpers so either `read`/`write` or `read_buf`/`write_buf` implementations can satisfy the same low-level request.

Directory flow uses `struct fuse_dh`. `opendir` allocates a high-level directory handle and stores it in the low-level file handle. `readdir` either writes directly into a response buffer when the filesystem supplies nonzero offsets, or stores a linked list of `fuse_direntry` records for later offset-based replay. `readdirplus` can call `do_lookup` for entries marked with `FUSE_FILL_DIR_PLUS`.

Shutdown in `fuse_destroy` restores an installed interrupt signal handler, creates a context for destroy callbacks, unlinks hidden nodes, frees every node from id table buckets, asserts slab lists are empty, unloads modules, frees hash tables/session/configuration, destroys locks, and deletes the thread-local context key.

## State And Persistence Behavior

The file maintains in-memory runtime state only. There is no disk persistence, but it has durable effects on the mounted filesystem and on backing files through user callbacks. Important mutable state includes the node id counter and generation, name and id hash tables, root and child nodes, lookup/reference counts, open counts, hidden-file flags, per-node lock lists, stat cache timestamps and sizes, LRU remembered-node ordering, module reference counts, and a global thread-local context key reference count.

Node tables use incremental split hashing. `hash_id`/`hash_name` grow and split tables when use reaches half of size; `unhash_id`/`unhash_name` can remerge and shrink when use falls below a quarter. With `FUSE_NODE_SLAB`, node memory comes from page-sized `mmap` slabs; otherwise it comes from `calloc`.

With `remember > 0`, forgotten nodes remain in `lru_table` until `fuse_clean_cache` ages them out. Single-threaded `fuse_loop` uses `fuse_session_loop_remember` with `poll` timeouts to clean remembered nodes, while multithreaded `fuse_loop_mt_312` starts `fuse_prune_nodes` as a cleanup thread.

Hidden-file state implements POSIX unlink semantics for open files. If `hard_remove` is disabled and an open file is unlinked or overwritten, libfuse renames it to `.fuse_hidden%08x%08x`, marks the node hidden, decrements visible link counts in getattr/statx replies, and unlinks the hidden path on final release or destroy.

## Dependencies And Integration Points

This file depends on public libfuse headers (`fuse.h`, `fuse_lowlevel.h`, `fuse_opt.h`) and internal headers (`fuse_i.h`, `fuse_kernel.h`, `fuse_misc.h`, `util.h`). It integrates directly with low-level session creation through `fuse_session_new_versioned`, request replies such as `fuse_reply_entry`, buffer utilities such as `fuse_buf_copy`, mount helpers via `fuse_session_mount`/`unmount`, and notification APIs through `fuse_lowlevel_notify_*`.

It also integrates with optional loadable modules. Built-ins `subdir` and, when configured, `iconv` are registered by factory symbol. Dynamic modules are loaded as `libfusemod_<name>.so` and searched for `fuse_module_<name>_factory`; factories can wrap the existing `fuse_fs` stack.

System dependencies include pthread mutexes, condition variables and thread-local keys; POSIX signals for interrupt handling; `dlopen`/`dlsym` for modules; `mmap` for node slabs; `poll` for the remembered-node single-thread loop; and standard filesystem types and constants.

## Risks And Edge Cases

The highest-risk area is path and node concurrency. Tree locks, queued waiters, hidden-file renames, `FORGET` handling, and multi-path operations such as rename must preserve parent/name consistency while callbacks may block or be interrupted. `try_get_path2` explicitly notes that locking two paths needs deadlock checking, so rename/link style operations deserve focused concurrency tests.

The node/name table implementation aborts on internal inconsistencies and relies on correct reference accounting. Incorrect `nlookup`, `refctr`, `open_count`, or LRU transitions can produce stale nodes, leaked nodes, premature deletion, or aborts. The slab allocator assumes page alignment when deriving a slab from a node pointer.

Callback return validation is limited. The code logs when reads or writes exceed requested size, but it still depends on filesystem implementations to follow high-level API contracts. Many wrappers treat absent callbacks as `-ENOSYS`, while release/opendir/open defaults are success; changing those semantics can break compatibility.

`fuse_destroy` iterates all modules with `while (fuse_modules) fuse_put_module(fuse_modules)`, which touches global module state, so module reference-count correctness matters across multiple `struct fuse` instances. `fuse_lib_help` loads modules to print help and does not visibly release every dynamically loaded module in that path.

Interrupt handling uses a signal sent to the worker thread once per second until the operation marks itself finished. This depends on signal handler setup, request interruption registration, and the callback being signal-aware or syscall-interruptible.

## Test Signals

Unit tests should exercise node lookup/forget/reference transitions, name and id hash growth/shrink behavior, path reconstruction with concurrent renames, hidden-file unlink/release flow, `remember` LRU expiry, and `lookup_path_in_cache` plus `fuse_invalidate_path` behavior. Callback wrapper tests should verify `-ENOSYS` defaults, private-data assignment, debug-safe formatting, buffer-vector fallback between `read`/`read_buf` and `write`/`write_buf`, and validation when callbacks return oversized reads or writes.

Integration tests should mount small high-level filesystems and drive lookup, create, open, read/write, readdir/readdirplus, rename including `RENAME_EXCHANGE`, xattrs, locks, ioctl, poll, fallocate, copy_file_range, lseek, statx, syncfs, and interrupt requests. Stress tests should combine multithreaded loops with rename/unlink/open/forget storms, remembered-node cleanup, module stacking, and forced interrupted open/create/opendir replies.
