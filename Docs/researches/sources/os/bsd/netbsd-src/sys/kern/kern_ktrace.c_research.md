# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ktrace.c

Read completely: 1494 lines.

Implements the core kernel tracing facility: trace descriptor management, asynchronous trace entry queueing, writer kthreads, trace record construction for many event classes, `fktrace(2)`, common trace attach/detach logic, authorization, and user trace records. The VFS path-based syscall wrapper lives in `kern_ktrace_vfs.c`.

Core structures:
- `struct ktrace_entry` contains a trace header, payload pointer/size, and small inline payload buffer.
- `struct ktr_desc` represents one trace output target, with flags, error accounting, refcount, queue count, delay/wakeup tuning, output file, writer LWP, entry queue, callout, and CVs.
- Global state includes `ktrace_lock`, `ktrace_on`, descriptor queue `ktdq`, entry pool cache, and a kauth listener.

Initialization and authorization:
- `ktrinit()` initializes `ktrace_lock`, creates the trace entry pool cache, and registers a process-scope kauth listener.
- `ktrace_listener_cb()` allows nonpersistent tracing for same real/effective/saved uid and gid relationships when the target is not persistent-traced or set-id; privileged and persistent decisions are deferred to secmodel policy.
- `ktrcanset()` asks kauth whether the caller may change tracing state on a target process.

Descriptor lifetime:
- `ktdref()` and `ktdrel()` maintain descriptor refs and global `ktrace_on`; the last release marks the descriptor done and wakes the writer thread.
- `ktd_lookup()` finds or references an existing descriptor for the same file, using `ktrsamefile()` to compare either identical file objects or matching underlying file type/data.
- `ktrderef()` clears a process trace pointer/flags, wakes sync waiters, and releases the descriptor.
- `ktradref()` adds a process reference to its trace descriptor.
- `ktrderefall()` clears all processes using a descriptor, optionally checking authorization for each.

Entry allocation and queueing:
- `ktealloc()` prevents recursive tracing with `ktrenter()`, allocates a trace entry and payload storage, initializes common header fields, timestamp, pid, command, trace format version, and LWP id.
- `ktraddentry()` handles deferred emulation records, references the descriptor, drops entries if tracing was cancelled/done or queue limit is exceeded, enqueues entries, optionally waits for writer drain under backpressure, schedules delayed writer wakeups, and frees entries on failure.
- `ktefree()` frees external payload buffers and returns entries to the pool.

Trace event producers:
- `ktr_syscall()` and `ktr_sysret()` record syscall arguments and returns.
- `ktr_namei()` and `ktr_namei2()` record path lookup strings, with optional emulation-root prefix.
- `ktr_emul()`, `ktr_execarg()`, `ktr_execenv()`, and `ktr_execfd()` record emulation and exec-related data.
- `ktr_sigmask()` records signal mask changes.
- `ktr_genio()`, `ktr_geniov()`, and `ktr_mibio()` record copied user I/O buffers through `ktr_io()`, chunking large payloads to page-sized records and yielding to preemption between chunks when needed.
- `ktr_psig()` records signal delivery and optional siginfo.
- `ktr_csw()` records context-switch out/in pairs while avoiding mutex/rwlock blocking points and interrupt/softint contexts.
- `ktruser()` implements user-provided `KTR_USER` records from user pointers; `ktr_kuser()` records kernel-provided user records; `ktr_mib()` records sysctl MIB names.
- `ktr_point()` tests the current process trace flag for one facility bit.

Trace control:
- `ktrace_common()` implements shared attach/detach behavior for path-based and fd-based interfaces. It handles clear-by-file, set with descriptor creation and writer thread startup, clear, process-group or pid targeting, descendant recursion, error/ref cleanup, and facility validation.
- `sys_fktrace()` obtains a writable file descriptor and calls `ktrace_common()`.
- `ktrops()` applies one trace operation to a process: authorizes, validates trace record version, installs or clears descriptor/facility bits, marks persistent tracing when authorized, schedules an emulation record when enabled, updates fast trace-enabled state, and reinterns syscalls if needed.
- `ktrsetchildren()` recursively walks a process tree under `proc_lock` and applies `ktrops()`.
- `sys_utrace()` is the syscall entry for user trace records.

Writer thread:
- `ktrace_thread()` waits for queued entries, detaches the whole queue, reports accumulated descriptor errors, writes entries, wakes synchronous waiters when drained, removes the descriptor from the global queue at shutdown, halts/destroys callouts, closes the output file, destroys CVs, frees the descriptor, and exits as a kthread.
- `ktrwrite()` batches headers and payloads into an iovec array, adapts header layout for trace versions 0 and 1, repeatedly calls the output file's `fo_write`, retries `EWOULDBLOCK`, stops tracing all users of the descriptor on other write errors, and frees written entries.

Concurrency and integration:
- `ktrace_lock` protects descriptors, queues, refs, and process trace pointer changes in combination with per-process locks and `proc_lock`.
- Trace producers use `ktrenter()`/`ktrexit()` recursion guards to avoid tracing trace writes or allocations recursively.
- Writer threads decouple traced processes from potentially blocking file writes while still offering synchronous waiting under queue pressure.
- Integrates with filedesc, kauth, kthreads, callouts, syscall intern hooks, signals, sysctl/MIB tracing, and ktrace version compatibility.

Risks and notes:
- Queue overflow logs `KTDE_ENOSPC` and drops entries; allocation failure TODOs remain in comments.
- Blocking writer detection sets `KTDF_BLOCKING` after timeout so traced processes are not stopped indefinitely.
- The writer-thread comment says ktrace descriptors cannot be watched by kqueue, then notes that is wrong for `fktrace`.
- `ktrace_common()` has a comment questioning why zero facilities are rejected at that point.
