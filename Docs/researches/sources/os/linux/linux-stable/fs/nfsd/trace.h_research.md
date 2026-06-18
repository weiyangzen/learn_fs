# File Research: sources/os/linux/linux-stable/fs/nfsd/trace.h

Purpose: defines the Linux tracepoint surface for NFSD. It is a trace-event catalog rather than runtime logic, covering request decode/encode errors, compound execution, filehandle verification, exports, VFS calls, I/O, state IDs, sessions, clients, filecache, duplicate reply cache, callbacks, nfsctl operations, server-side copy, xattrs-adjacent VFS operations, and pNFS fencing.

Key structures and state:
- Uses tracepoint macros such as `TRACE_EVENT`, `TRACE_EVENT_CONDITION`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, and `TRACE_DEFINE_ENUM`.
- Common field/assignment macros capture network namespace inode, RPC XID, server/client socket addresses, procedure status, filehandle hashes, stateid components, and NFSD permission flags.
- Includes NFSD internals (`state.h`, `filecache.h`, `vfs.h`, `cache.h`) only after early trace definitions that need lighter dependencies.
- Symbol printers translate NFSD access bits, file types, stateid types/statuses, session flags, callback state/opcodes, RPC auth flavors, filecache flags, duplicate reply cache outcomes, and recall-any masks.

Major logic:
- XDR and compound tracepoints record garbage args, encode failures, op decode failures, operation status, and nontrivial compound errors.
- Filehandle/export tracepoints record verification attempts, verification failures, export-key lookup/update, export-by-name lookup, and export cache updates.
- I/O tracepoints distinguish read/write start, splice/vector/direct paths, I/O completion, commit, and read/write error reporting.
- NFSv4 state tracepoints cover stateid allocation/free/revoke, replay, session sequence status, create-session slot sequencing, client confirmation/expiry/reclaim, verifier and credential mismatches, and grace lifecycle.
- Filecache tracepoints expose file allocation, acquisition, open/opened, cache lookup, fsnotify invalidation, LRU/GC/shrinker activity, close, and DIO alignment attributes.
- Callback tracepoints cover setup, lifecycle queue/restart/destroy, backchannel update/shutdown, CB_SEQUENCE slot state, delegation/layout/offload/getattr/notify-lock callbacks, and callback completion.
- Control-plane tracepoints cover `/proc/fs/nfsd`-style actions: unlock IP/fs, filehandle generation, thread pool changes, version/port/block-size/minthreads/time/recoverydir settings, grace end, and filehandle key changes.
- Server-side copy tracepoints capture intra/inter/async copy request state, source/destination/callback stateids, offsets/counts, completion, cancellation, and clone errors.
- Final pNFS tracepoint class records fencing errors by client, netns, device string, and error.

Concurrency and lifetime:
- Tracepoints copy strings, socket addresses, flags, stateids, and verifier bytes into trace entries during `TP_fast_assign`, avoiding later dereference of mutable kernel state.
- Several tracepoints intentionally store pointers only for identity/debug output and label them as not dereferenceable.
- Conditional tracepoints avoid unsafe contexts, for example filehandle verification events require a non-NULL request and callback recall requires a client pointer.

Important dependencies:
- Depends on kernel tracing APIs and shared trace helpers from `trace/misc/fs.h`, `trace/misc/nfs.h`, and `trace/misc/sunrpc.h`.
- Closely follows structures from NFSD export, filehandle, NFSv4 XDR, state, filecache, VFS, and duplicate reply cache code.
- Provides the event names consumed by NFSD implementation files such as `vfs.c`, `nfs4callback.c`, `nfs4state.c`, `filecache.c`, and nfsctl code.

Risk/edge cases:
- Tracepoint field layouts are tightly coupled to NFSD structure fields; structure churn can silently make trace output misleading if not updated.
- Some events expose client addresses, export paths, filenames, symlink targets, verifier bytes, and auth flavor information through tracing.
- Socket address length arguments must match local/remote address fields; most events take care to use transport-provided lengths.
