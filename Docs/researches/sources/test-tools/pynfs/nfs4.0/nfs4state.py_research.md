# sources/test-tools/pynfs/nfs4.0/nfs4state.py

## Purpose
`nfs4state.py` supplies the in-memory state engine and virtual filesystem used by the Python NFSv4 server. It models client ID caches, NFSv4 stateids, open owners, lock owners, share reservations, POSIX-like byte-range locks, virtual filehandles, attributes, ACL mapping, hard links, directory cookies, and an optional hard-backed filehandle implementation. It is the semantic core behind `nfs4server.py` operations.

## Important APIs, Types, And Functions
- `NFS4Error(code, msg=None, attrs=0, lock_denied=None)` carries NFS status codes plus partial attribute masks and lock-denied payloads.
- `mod32`, `converttime`, `packnumber`, `unpacknumber`, and `printverf` implement protocol-sized counters, NFS time values, and verifier/stateid byte strings.
- Global `InstanceKey` and `Mutate()` influence generated filehandle bytes; global `POSIXLOCK` and `POSIXACL` select lock and ACL semantics.
- `NFSServerState` owns protocol state: confirmed/unconfirmed `ClientIDCache`, `state` dict of internal IDs to `StateIDInfo`, server `instance`, `write_verifier`, `openowners`, `lockowners`, and root handle for lease time.
- `ClientIDCache` stores `(client verifier, client owner id, clientid, callback, server verifier, principal, time)` entries and supports matching, renewal, expiry, and removal.
- `OwnerInfo` stores per-open-owner or per-lock-owner sequence state, cached replay response, confirmation flag, lockowner/openid linkage, and file-to-state-id mappings.
- `NFSServerState.check_seqid`, `advance_seqid`, `confirm`, `open`, `close`, `new_lockowner`, `lock`, `testlock`, `unlock`, `check_read`, `check_write`, `downgrade`, `renew`, and `remove_state` are the main server-facing operations.
- `NFSFileState` owns per-file share and lock state. It converts two-bit NFS share masks to internal three-bit values, detects share conflicts, checks access, adds/removes/merges locks, and tests conflicts.
- `NFSFileHandle` is an abstract-ish base for NFS-visible objects. `VirtualHandle` implements the RAM filesystem; `HardHandle` wraps real OS paths for limited hard-backed use.
- `VirtualHandle.supported` maps NFS attribute numbers to read/write/not-supported flags, driving both `get_attributes` and `set_attributes`.
- `DirList` stores directory entries with monotonically increasing cookies and a verifier for READDIR.

## Control Flow
Client setup starts in `NFSServerState.new_clientid`, `ClientIDCache.add`, and the server's SETCLIENTID/CONFIRM handlers. Confirmed client IDs renew leases through explicit `renew` and implicit `__renew` calls whenever stateids are used. Open owner and lock owner sequence IDs are validated with `check_seqid`; accepted responses are cached in `advance_seqid` for replay handling.

Open state flows from `open(fh, owner, access, deny)`. The method resolves or creates an `OwnerInfo`, handles unconfirmed open-owner replacement rules, allocates an internal numeric state ID for the `(owner, fh)` pair, asks the file's `NFSFileState` to test and add share reservations, and returns a generated `stateid4`. Open confirmation marks the owner confirmed and returns a fresh stateid. Close removes locks associated with the open, removes share reservations, deletes owner file mappings, marks the state entry closed, and renews the lease.

Stateid translation is centralized in private helpers. `__state2id` recognizes special all-zero and all-ones stateids, rejects stateids from older server instances with `NFS4ERR_STALE_STATEID`, rejects unknown IDs with `NFS4ERR_BAD_STATEID`, and can detect old stateid sequence numbers. `__stateid` increments the stored stateid seqid, combines server instance bytes with packed internal ID bytes, and renews the lease.

Lock flow resolves either a new lock owner or existing lock stateid to an internal ID, validates range length and overflow with `__getlockend`, checks conflicts through `__testlock`, records the lock in the file's `NFSFileState`, confirms the lock owner, and returns a new lock stateid. `LOCKT` creates or resolves a test owner, checks client ID freshness, and tests conflicts without changing the server's effective lock table. `check_read` and `check_write` combine open share access checks with range lock conflict checks; when passed an open stateid they include all lock stateids tied to that open owner.

The RAM filesystem starts with `VirtualHandle`. Construction sets default attributes, initializes `DirList` for directories, `StringIO` plus `NFSFileState` for regular files, link target state for symlinks, or raw device data for block/char nodes. `create` validates directory context, creates a child `VirtualHandle`, filters attributes inappropriate for the type, applies attributes through `set_attributes`, inserts it into the `DirList`, and updates change/time/size fields. `read`, `write`, `remove`, `rename`, `hardlink`, `lookup`, `read_dir`, `read_link`, and `do_lookupp` implement object operations used by the server handlers.

Attribute flow uses the `supported` table. `set_attributes` rejects unknown, read-only, or explicitly unsupported attrs, applies custom setters such as `set_fattr4_size`, `set_fattr4_time_modify_set`, `set_fattr4_time_access_set`, and `set_fattr4_acl`, updates metadata time/change counters, and returns a bitmap of successfully set attrs. `get_attributes` ignores unknown/unreadable attrs and either ignores or errors on not-supported attrs depending on the caller's `ignore` flag.

## State And Persistence Behavior
All primary state is process memory. Client IDs encode `self.instance`, which is derived from process start time; stateids also embed that instance. A restart causes old client IDs and stateids to become stale or bad. Virtual files store bytes in `StringIO`, directory entries in `DirList`, attributes on object instances, ACLs as generated pynfs ACL structures, and locks/shares in `NFSFileState`. There is no disk synchronization or crash recovery. `HardHandle` can read/write real filesystem paths but is incomplete and separate from the default server path.

## Dependencies And Integration Points
The module imports generated NFSv4 XDR constants/types, `rpc.rpc`, `nfs4acl`, `nfs4lib`, `sha`, `stat`, and OS/time/random/string helpers. It is tightly integrated with `nfs4server.py`, which catches `NFS4Error`, calls `NFSServerState` for protocol state, and invokes `VirtualHandle` methods for filesystem semantics. ACL behavior delegates to `nfs4acl.maps_to_posix`, `acl2mode`, and `mode2acl`. Attribute names and bitmaps rely on `nfs4lib`.

## Risks And Edge Cases
- The file mixes Python 2 idioms (`long`, `array.tostring`, `string.join`, `sha`, old exception syntax in one `except`) with Python 3-looking callers, which is a portability risk.
- Several errors are raised as strings, not exceptions; this is invalid in Python 3 and fragile even in Python 2-era code.
- `ClientIDCache.remove` deletes while iterating a zipped range/list snapshot and removes only matching indices from the live list, which is brittle for multiple matches.
- `DirList.__setitem__` tries `del self.list[x]` where `x` is a `DirEnt`, not an index, in the duplicate-name branch.
- `NFSFileState.addposixlock` and `removeposixlock` call `list.sort()` on `LockInfo` objects that define `__cmp__`, not rich comparisons, which is another Python 3 conversion risk.
- `check_read` and `check_write` have FIXME notes around reserved stateids and rely on simplified share semantics.
- `VirtualHandle.get_attributes` silently ignores unknown and some unreadable attrs, which may not match strict server behavior tests for write-only attributes.
- Hard-backed `HardHandle` is incomplete: constructor argument order in `read_dir` appears inconsistent, supported attrs are limited, and directory cache initialization is not obvious.

## Test Signals
The associated server tests exercise this module indirectly. Close tests validate sequence IDs, bad/old/stale stateids, lease expiry, lock release on close, and replay. Lock and LOCKT tests validate lock conflict detection, range overflow, zero length, stateid freshness, share/open mode interactions, POSIX lock merge/split behavior, and lease expiry cleanup. CREATE/LINK/GETATTR/GETFH/COMMIT tests validate virtual file type handling, attributes, link counts, directory cookies, and filehandle generation. ACL tests specifically signal `set_fattr4_acl` and POSIX ACL mapping behavior.
