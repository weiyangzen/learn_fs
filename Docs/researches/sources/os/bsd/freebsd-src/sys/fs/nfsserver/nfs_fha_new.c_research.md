# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_fha_new.c

## Purpose
Implements the NFS server File Handle Affinity scheduler for NFSv2/v3 requests. FHA assigns incoming RPC requests to `nfsd` service threads based on file-handle identity, read/write offset locality, exclusive-vs-shared operation class, and per-file/per-thread load limits.

## Main Interfaces
- `fhanew_assign(SVCTHREAD *this_thread, struct svc_req *req)` chooses and locks the service thread that should receive a request.
- `fhanew_nd_complete(SVCTHREAD *thread, struct svc_req *req)` releases request accounting after the operation completes.
- VNET init/uninit functions allocate/destroy per-vnet FHA state.
- Sysctls under `vfs.nfsd.fha` expose enable, read-locality, write-locality, bin shift, max nfsds per file handle, max requests per nfsd, and a text stats dump.

## Key Behavior
- Initialization allocates `struct fha_params`, initializes `FHA_HASH_SIZE` slot mutexes, sets server name `nfsd`, and loads default tuning values from the header.
- Request extraction accepts only NFS program requests for versions 2 and 3. NFSv2 procedure numbers are translated to v3-style procedure numbers through `newnfs_nfsv3_procid`.
- File handles are parsed from the request XDR without blocking. The scheduler compresses a variable-length file handle into a 64-bit affinity key by XORing bytes into rotating 8-byte lanes.
- Read/write offsets are parsed for `READ` and `WRITE`; requests without meaningful offsets keep offset zero. Procedures are classified as shared or exclusive based on whether they can contend over file state.
- `fha_hash_entry_lookup()` finds or creates a per-file-handle hash entry under the appropriate slot mutex.
- Thread selection prefers an already-associated thread when exclusive operations are active, otherwise tries locality within `1 << bin_shift` bytes, respecting `max_reqs_per_nfsd`. If no locality match is available, it either attaches the current thread up to `max_nfsds_per_fh` or chooses the least-loaded existing thread.
- Assignment stores the file-handle entry and operation metadata in `svc_req` scratch fields, increments per-entry and per-thread counters, records the offset in `SVCTHREAD::st_p3`, and returns with the selected thread lock held.
- Completion decrements shared/exclusive and thread request counters, removes idle threads from the file-handle entry, and deletes the entry when no requests or threads remain.
- The stats sysctl walks all hash slots and prints file-handle entries, shared/exclusive counts, thread counts, thread offsets, and per-thread request counts.

## Important State
- Uses VNET-local `fhanew_softc` and `nfsfha_ctls`.
- `struct fha_hash_entry` tracks one affinity file handle, number of shared/read-write operations, number of exclusive operations, associated service threads, and its slot mutex.
- `SVCTHREAD` scratch fields are used for FHA state: `st_p2` is per-thread outstanding request count for an entry and `st_p3` is last offset; `svc_req` scratch fields hold the hash entry, lock type, and offset.

## Dependencies
Depends on FreeBSD RPC server thread/request structures, NFS XDR helpers (`NFSM_DISSECT_NONBLOCK`, `newnfs_realign`, `fxdr_hyper`), NFS procedure constants, VNET sysinit/sysuninit, sysctl/sbuf APIs, mutex/list primitives, and the shared header `nfs_fha_new.h`.

## Risks and Edge Cases
- FHA only applies to NFSv2/v3. NFSv4 or non-NFS RPCs fall back to the current service thread.
- Request parsing is best-effort; malformed or unsupported requests get a synthetic incrementing file-handle key and exclusive default behavior.
- The scheduler stores state in generic RPC scratch fields, so it depends on no other server layer reusing those fields for the same request/thread lifecycle.
- Hash entries are destroyed only when both operation counts and associated thread counts reach zero; accounting mismatches trigger assertions or leaks.
- Offset locality is only approximate because file handles are compressed into 64 bits and locality is measured by last thread offset rather than full per-stream history.
