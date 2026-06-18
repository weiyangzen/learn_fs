# File Research: sources/os/linux/linux/fs/smb/client/smb2ops.c

## Scope
Read completely: 5,980 lines. This file implements SMB2/SMB3 dialect-specific operation glue for the Linux CIFS/SMB client. It binds common CIFS VFS behavior to SMB2-family wire operations, including credit management, compound request construction, multichannel support, copy offload, sparse/range operations, leases/oplocks, encryption transforms, and dialect operation/value tables.

## High-Level Role
`smb2ops.c` is the SMB2+ implementation of the client’s `struct smb_version_operations` and `struct smb_version_values` dispatch layer. Higher-level CIFS code calls through these operation tables; this file selects SMB2.0, SMB2.1, SMB3.0, and SMB3.1.1 behavior and points many entries at helpers implemented here or in companion SMB2 files.

## Main Functional Areas

### Credit and MID Management
Lines 34-381 implement SMB2 credit accounting:
- `change_conf()` reserves or releases credits for echoes and oplock breaks.
- `smb2_add_credits()` returns credits after responses, detects reconnect-instance mismatch, rebalances echo/oplock credits, caps server credits at 65,000, updates `in_flight`, wakes waiters, and traces credit changes.
- `smb2_set_credits()` resets credit state on reconnect and advances reconnect/channel sequence counters.
- `smb2_wait_mtu_credits()` reserves credits for large MTU reads/writes while leaving a small reserve for reopen and control operations.
- `smb2_adjust_credits()` returns unused read/write credits after a short transfer and rejects adjustment across reconnect instances.

Lines 383-443 implement MessageId helpers:
- `smb2_get_next_mid()` allocates current `MessageId`.
- `smb2_revert_current_mid()` rolls back unused MIDs.
- `__smb2_find_mid()` locates pending MID entries by wire MID and command, optionally dequeuing them.

### Negotiation and I/O Size Selection
Lines 461-592 handle negotiation state and read/write sizing:
- `smb2_need_neg()` treats `server->max_read == 0` as needing negotiation.
- `smb2_negotiate()` resets MID allocation before `SMB2_negotiate()`.
- `smb2_negotiate_wsize()` / `smb2_negotiate_rsize()` apply SMB2 defaults and large-MTU limits.
- SMB3 variants use larger defaults and account for SMB Direct/RDMA fragment limits and encryption header overhead.

### Multichannel Interface Discovery
Lines 594-880 parse and request server network interface information:
- `iface_cmp()` sorts preferred interfaces by RDMA capability, RSS capability, speed, then address.
- `parse_server_interfaces()` parses `FSCTL_QUERY_NETWORK_INTERFACE_INFO`, normalizes ports from the connected server address, maintains `ses->iface_list`, marks inactive entries, validates `Next` offsets, and handles empty lists.
- `SMB3_request_interfaces()` rate-limits interface queries and updates channel-interface association if the current channel’s interface becomes inactive.

### Share and Filesystem Metadata
Lines 882-956 query share capabilities and filesystem metadata during tree connect:
- `smb3_qfs_tcon()` opens the share root, preferably through cached directory state, requests interfaces, and queries attribute/device/volume/sector info.
- `smb2_qfs_tcon()` performs the simpler SMB2 filesystem queries.

Lines 2988-3062 implement `statfs`:
- `smb2_queryfs()` issues a compound query for `FS_FULL_SIZE_INFORMATION`, validates output bounds, fills `kstatfs`, and sets `SMB2_SUPER_MAGIC`.
- `smb311_queryfs()` uses POSIX qfs info when SMB3.1.1 POSIX extensions are active.

### Path Accessibility and File Info
Lines 958-1043:
- `smb2_is_path_accessible()` probes a path with open/close, handles cached directories, maps invalid DFS-link names, and respects `CIFS_MOUNT_NO_DFS`.
- `smb2_get_srv_inum()` maps server index number to unique inode id.
- `smb2_query_file_info()` queries by open file handle and carries cached symlink target into the returned open-info data.

### Extended Attributes
Under `CONFIG_CIFS_XATTR`, lines 1045-1366 implement EA query/set:
- `move_smb2_ea_to_cifs()` converts SMB2 full-EA entries to Linux xattr semantics, adding `user.` prefixes for listxattr and validating each entry’s bounds.
- `smb2_query_eas()` performs compound open/query/close and validates the returned EA buffer.
- `smb2_set_ea()` builds a create/set-info/close compound, validates EA name length, optionally pre-queries EA space, handles encryption flags, and retries replayable failures with SMB3 replay flags.

### Stats, FIDs, Close, and Copy Offload
Lines 1368-1542:
- `smb2_can_echo()`, `smb2_clear_stats()`, `smb2_dump_share_caps()`, and `smb2_print_stats()` expose mount diagnostics.
- `smb2_set_fid()` records persistent/volatile FIDs, access, debug MID, lease/oplock state, cache flags, and create GUID.
- `smb2_close_file()` wraps close; `smb2_close_getattr()` closes and updates inode time/allocation metadata from close response.

Lines 1544-2069 implement server-side copy:
- `SMB2_request_res_key()` obtains `FSCTL_SRV_REQUEST_RESUME_KEY`.
- `calc_chunk_count()` derives safe copychunk fanout from tcon limits.
- `smb2_copychunk_range()` issues `FSCTL_SRV_COPYCHUNK_WRITE`, splits large ranges, adapts to server-reported smaller limits, validates response size and counts, rewinds partial copies, and traces copy success/failure.

### Sync I/O, Sparse Files, Clone, Compression, Integrity
Lines 2071-2274:
- Read/write data offset/length helpers parse SMB2 read response fields.
- `smb2_sync_read()` and `smb2_sync_write()` inject persistent/volatile FIDs into common SMB2 read/write calls.
- `smb2_set_sparse()` toggles sparse-file state with `FSCTL_SET_SPARSE` and caches broken sparse support.
- `smb2_set_file_size()` marks large extensions sparse before setting EOF.
- `smb2_duplicate_extents()` implements clone/dedupe-style extent duplication via `FSCTL_DUPLICATE_EXTENTS_TO_FILE`, extending destination size if needed.
- `smb2_set_compression()` and `smb3_set_integrity()` wrap compression/integrity SMB2/SMB3 controls.

### Snapshots, Change Notify, Directory Enumeration
Lines 2276-2450:
- `smb3_enum_snapshots()` performs two-phase snapshot enumeration with Azure-compatible minimal first response sizing and copies bounded output to userspace.
- `smb3_notify()` opens a path, issues change notify, and optionally returns change records to userspace.

Lines 2452-2608:
- `smb2_query_dir_first()` constructs an open/query-directory compound, handles replay, records returned FID, handles `STATUS_NO_MORE_FILES`, increments remote open count, and parses the first directory page.
- `smb2_query_dir_next()` and `smb2_close_dir()` wrap follow-up query and close.

### Status Handling and Compound Request Helpers
Lines 2610-2822:
- `smb2_is_status_pending()` handles `STATUS_PENDING` interim responses and credits returned with them.
- `smb2_is_session_expired()` detects session expiry/deletion status.
- `smb2_is_status_io_timeout()` and `smb2_is_network_name_deleted()` map notable server errors and mark matching tcons for reconnect.
- `smb2_oplock_response()` acknowledges lease/oplock breaks.
- `smb2_set_replay()`, `smb2_set_related()`, and `smb2_set_next_command()` set SMB3 replay, compound related-operation flags, and 8-byte compound alignment. Encrypted compounds are flattened because the encryption layer cannot handle padding iovs.
- `smb2_should_replay()` implements exponential backoff for replayable operations.

### Generic Compound Query Helper
Lines 2824-2986 implement `smb2_query_info_compound()`, a reusable open/query-info/close compound path. It can use cached root-directory FIDs for root queries, supports encryption, replay, response ownership transfer to the caller, and marks tcon reconnect on `-EREMCHG`.

### DFS and ACL Handling
Lines 3100-3205 implement DFS referrals through `FSCTL_DFS_GET_REFERRALS`, preferring IPC tcon and retrying transient errors once.

Lines 3207-3377 implement SMB2 ACL operations:
- `get_smb2_acl_by_fid()` queries ACL from an already-open FID.
- `get_smb2_acl_by_path()` opens the target, using `OPEN_REPARSE_POINT` so symlink ACLs apply to the link itself.
- `set_smb2_acl()` opens with access flags derived from owner/group/DACL/SACL writes and sends set-ACL.
- `get_smb2_acl()` chooses an existing readable open file when possible unless SACL access is requested.

### Range, Allocation, SEEK_DATA/HOLE, FIEMAP
Lines 3379-4078 implement fallocate-style operations over SMB3 primitives:
- `smb3_zero_range()` invalidates/writebacks local cache, calls `FSCTL_SET_ZERO_DATA`, and updates EOF/netfs/fscache state when extending.
- `smb3_punch_hole()` ensures sparse state, invalidates cache, sends zero-data FSCTL, and updates remote size when dirty local data extended EOF.
- `smb3_simple_falloc()` handles allocation emulation by EOF extension, sparse toggling, or bounded zero writes.
- `smb3_collapse_range()` and `smb3_insert_range()` emulate range movement with server-side copychunk and EOF updates.
- `smb3_llseek()` implements `SEEK_DATA`/`SEEK_HOLE` using `FSCTL_QUERY_ALLOCATED_RANGES`, flushing pending writes first.
- `smb3_fiemap()` translates allocated-range responses into fiemap extents, continuing after `-E2BIG`.
- `smb3_fallocate()` dispatches Linux fallocate modes to the above implementations.

### Oplocks, Leases, and Lease Contexts
Lines 4080-4327:
- SMB2 oplock setters map protocol oplock levels to CIFS cache flags.
- SMB2.1/SMB3 lease setters parse R/H/W lease bits and manage epoch-based cache purge decisions.
- Lease creation helpers build `RqLs` create contexts for SMB2 lease v1 and SMB3 lease v2, including parent lease keys.
- Lease parse helpers recover state, epoch, and lease key.
- `smb2_wp_retry_size()` bounds writepage retry size to SMB2 max buffer.

### Encryption and Transform Processing
Lines 4335-5209 implement SMB3 encryption/decryption:
- `fill_transform_hdr()` builds SMB3 transform headers, choosing GCM/CCM nonce sizes and copying session id.
- `smb2_aead_req_alloc()` and `smb2_get_aead_req()` allocate aligned AEAD request, IV, and scatterlist storage, then map request iovs/iter data/signature into SG entries.
- `smb2_get_enc_key()` finds session encryption/decryption keys on the primary server/session list.
- `crypt_message()` performs AEAD encrypt/decrypt for AES-CCM/GCM, selects 128/256-bit key size, sets auth tag size, and copies signatures.
- `smb3_init_transform_rq()` creates encrypted compound request arrays, copying iterator data into folio queues before encryption.
- `decrypt_raw_data()` decrypts received transform frames, with optional per-work-item crypto transform for offloaded decryption.
- `handle_read_data()` validates and copies SMB2 read response payloads from header buffer or folio queue into the request iterator, handles pending/session-expired/error states, and dequeues or marks mids.
- `receive_encrypted_read()` reads large encrypted READ responses into folio queues and may offload decryption to `decrypt_wq`.
- `receive_encrypted_standard()` decrypts standard encrypted frames and splits compound responses by `NextCommand`.
- `smb3_receive_transform()` validates transform sizes and chooses large-read or standard encrypted receive handling.
- `smb3_handle_read_data()` is the non-transform read-data entry point.

### Special Node Creation
Lines 5211-5399:
- `smb2_next_header()` computes next SMB header offsets for normal and transform headers with overflow/min-size checks.
- `__cifs_sfu_make_node()` creates SFU-emulated special files by writing type tags and device/symlink payloads into a system file, cleaning up intermediate objects on failure.
- `cifs_sfu_make_node()` instantiates the dentry after SFU creation by querying inode info through POSIX, UNIX, or normal CIFS paths.
- `smb2_make_node()` chooses SFU emulation or reparse-point mknod support depending on mount/server capabilities.

## Dialect Operation Tables
Lines 5401-5838 define `struct smb_version_operations` tables:
- `smb20_operations` is conditional on insecure legacy support and uses SMB2.0 helpers, basic oplocks, SMB2 sizing, no SMB3 transform support.
- `smb21_operations` adds SMB2.1 leases, MTU credit wait/adjust, snapshots/notify, and EA/ACL helpers.
- `smb30_operations` switches to SMB3 sizing, share capability dumping, SMB3 lease/oplock handling, multichannel interface query, close-getattr, integrity, duplicate extents, validate-negotiate, fallocate, encryption transform init/receive, and SMB3 signing key generation.
- `smb311_operations` is similar to SMB3.0 but uses SMB3.1.1 signing keys, POSIX mkdir, POSIX qfs when enabled, and omits SMB3 validate-negotiate as unused for 3.1.1.

## Dialect Value Tables
Lines 5840-5980 define `struct smb_version_values`:
- SMB2.0 and SMB2.1 use SMB2 protocol IDs, SMB2 header/read response sizes, SMB2 locks, basic capabilities, and lease v1 create context size.
- `smb3any_values` and `smbdefault_values` advertise broad SMB3 capabilities for dialect negotiation arrays.
- SMB3.0, SMB3.0.2, and SMB3.1.1 use SMB3 capability masks including DFS, leasing, large MTU, persistent handles, encryption, and directory leasing, and use lease v2 create context size.

## Concurrency and State Notes
The file uses several lock domains:
- `server->req_lock` protects credits and `in_flight`.
- `server->mid_counter_lock` protects MID allocation.
- `server->mid_queue_lock` protects pending MID queues.
- `server->srv_lock` protects TCP status checks.
- `ses->iface_lock` and `ses->chan_lock` protect multichannel interface/channel state.
- `cifs_tcp_ses_lock` protects session/tcon lists.
- inode/page-cache paths use `filemap_invalidate_lock()`, inode `i_lock`, netfs resize helpers, and fscache cookie resize to keep local state consistent with server-side range operations.

## Error Handling and Replay Behavior
The file is defensive around malformed server data:
- It validates interface `Next` offsets, EA entry sizes, query-info buffers, copychunk response lengths/counts, encrypted transform sizes, read payload offsets/lengths, and allocated-range response alignment.
- Replayable compound operations reinitialize request state, mark `SMB2_FLAGS_REPLAY_OPERATION`, and use exponential backoff through `smb2_should_replay()`.
- Reconnect-instance checks prevent returning credits to stale sessions.
- Share deletion and session expiry paths mark reconnect state or trigger reconnect handling.

## Security-Relevant Behavior
Security-sensitive areas include:
- SMB3 encryption/decryption with AEAD and per-session keys.
- Passthrough FSCTL and SET_INFO ioctl paths requiring `CAP_SYS_ADMIN`.
- ACL queries/sets using `READ_CONTROL`, `WRITE_DAC`, `WRITE_OWNER`, and `SYSTEM_SECURITY`.
- Symlink/reparse ACL querying intentionally opens reparse points rather than targets.
- DFS, xattr, snapshot, notify, and passthrough paths copy bounded data to/from userspace and perform explicit buffer validation.

## External Dependencies
This file relies heavily on adjacent SMB client components:
- SMB2 PDU builders and wire calls such as `SMB2_open`, `SMB2_ioctl`, `SMB2_query_info_init`, `compound_send_recv`, `SMB2_close`, `SMB2_read`, and `SMB2_write`.
- CIFS VFS state types from `cifsglob.h`, `cifsproto.h`, `smb2proto.h`, `smb2pdu.h`, `cached_dir.h`, `reparse.h`, and `fscache.h`.
- Linux crypto AEAD, scatterlists, folio queues, netfs helpers, page-cache invalidation, and userspace copy APIs.

## Research Takeaways
`smb2ops.c` is a central dialect-adapter file rather than a single feature module. Its highest-risk areas are credit accounting, compound replay, encrypted receive/decrypt handling, and cache-coherent server-side range modification. Its operation tables at the end are the main index for understanding which SMB2/SMB3 protocol features are active for each dialect.
