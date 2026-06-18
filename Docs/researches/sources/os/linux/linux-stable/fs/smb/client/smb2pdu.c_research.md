# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2pdu.c

## Summary
Implements the SMB2/SMB3 protocol worker layer for the Linux CIFS client. It constructs and sends most SMB2 PDUs, handles reconnect/replay gating, negotiates dialects and negotiate contexts, performs session setup and tree connect/disconnect, opens and closes file handles, sends query/set/IOCTL/lock/read/write/flush/directory/lease/oplock requests, parses create and POSIX contexts, and bridges SMB3 features such as encryption, multichannel, persistent handles, compression, leases, POSIX extensions, and SMB Direct read/write offload.

## Main Responsibilities
- Assemble SMB2 headers, fixed command bodies, variable buffers, and create/query contexts with the protocol-required alignment and length fields.
- Decide when SMB3 encryption is required from session flags, share flags, mount `seal`, global security flags, and server capabilities.
- Coordinate reconnects before sending handle-independent commands, including session setup, tree reconnect, multichannel rescaling, interface queries, and persistent-handle reopen scheduling.
- Negotiate SMB2/SMB3 dialects, SMB 3.1.1 preauth/encryption/signing/compression/POSIX contexts, server capabilities, max I/O sizes, security mode, and AEAD crypto setup.
- Run session setup using Kerberos upcall or raw NTLMSSP challenge/authenticate flows, including channel binding behavior.
- Connect and disconnect trees, validate negotiate info for SMB3 dialects before 3.1.1, and initialize share attributes such as capabilities, encryption, copychunk defaults, and isolated transport.
- Build `CREATE` requests with path conversion, DFS prefixing, leases, durable/persistent handle contexts, POSIX mode contexts, snapshot timewarp, security descriptor mode/owner contexts, query-id contexts, and EA contexts.
- Parse `CREATE` response contexts for leases, query-on-disk IDs, and SMB3 POSIX response data.
- Provide synchronous and asynchronous read/write paths, including netfs completion callbacks, credit accounting, replay decisions, signature verification, stats, EOF handling, compression flags, and optional SMB Direct memory registration.
- Implement `IOCTL`, `QUERY_INFO`, `SET_INFO`, `QUERY_DIRECTORY`, `CHANGE_NOTIFY`, `LOCK`, `FLUSH`, `CLOSE`, `ECHO`, `OPLOCK_BREAK`, `LEASE_BREAK`, and filesystem-info helpers.

## Key Interfaces
- Core negotiation/session/tree APIs: `SMB2_negotiate()`, `smb3_validate_negotiate()`, `smb2_select_sectype()`, `SMB2_sess_setup()`, `SMB2_logoff()`, `SMB2_tcon()`, and `SMB2_tdis()`.
- Reconnect and channel handling: `smb3_update_ses_channels()`, `smb2_reconnect_server()`, and the internal `smb2_reconnect()` path.
- Open/create APIs: `SMB2_open_init()`, `SMB2_open()`, `SMB2_open_free()`, `smb311_posix_mkdir()`, `smb2_parse_contexts()`, `posix_info_sid_size()`, and `posix_info_parse()`.
- Request families: `SMB2_ioctl[_init/_free]()`, `SMB2_close[_init/_free]()`, `SMB2_flush[_init/_free]()`, `SMB2_query_info[_init/_free]()`, `SMB2_query_acl()`, `SMB2_get_srv_num()`, `SMB2_query_directory[_init/_free]()`, `SMB2_set_info_init()`, `SMB2_set_eof()`, `SMB2_set_acl()`, `SMB2_set_ea()`, `SMB2_QFS_attr()`, and `SMB311_posix_qfs_info()`.
- I/O APIs: `smb2_async_readv()`, `SMB2_read()`, `smb2_async_writev()`, and `SMB2_write()`.
- Lock and cache-control APIs: `SMB2_lock()`, `smb2_lockv()`, `SMB2_oplock_break()`, `SMB2_lease_break()`, `SMB2_change_notify()`, `SMB2_echo()`, and `SMB2_set_compression()`.
- Validation helpers: `smb2_validate_iov()`, `smb2_validate_and_copy_iov()`, `smb2_copy_fs_info_to_kstatfs()`, and SMB3 encryption predicate `smb3_encryption_required()`.

## Control Flow And Behavior
Requests are normally built through `smb2_plain_req_init()`, which first runs reconnect gating, allocates either a small or large CIFS buffer based on command type, fills the SMB2 header, initializes structure size, and increments per-tcon SMB2 command stats. IOCTL initialization can skip reconnect for validate-negotiate and reconnect-time interface queries to avoid recursion.

Reconnect handling rejects sends while tcons or sessions are exiting, waits for transport reconnect, serializes session reconnect under `session_mutex`, renegotiates dialect/session state, handles servers that lose multichannel support, tree-connects again when needed, marks open files invalid, schedules persistent-handle reopen, queries interfaces, adjusts channels, and returns `-EAGAIN` for handle-based commands that the caller must retry with a known-good handle.

Negotiation builds dialect lists for `vers=default`, `vers=3`, and explicit dialects. SMB 3.1.1 adds negotiate contexts for preauth integrity, encryption, netname, POSIX extension availability, optional compression, and optional signing capabilities. The response is checked against the requested dialect set, security mode and capability state are recorded, signing is enabled if required, GSS/NTLMSSP blobs are decoded, 3.1.1 contexts are parsed, and AEAD crypto transforms are allocated when encryption is negotiated.

Session setup is state-machine based. Raw NTLMSSP allocates an NTLMSSP context, sends negotiate, decodes challenge, sends authenticate, stores the session id and flags unless this is channel binding, and generates signing/encryption keys. Kerberos uses `cifs_get_spnego_key()`, validates the upcall format, pads short GSS session keys to the SMB2 minimum, sends the security blob, and establishes session keys. Sensitive buffers are explicitly zeroed or freed through sensitive cleanup paths.

Create/open request construction is the densest part of the file. Paths are UTF-16 converted, optionally prefixed with tree name for DFS operations, padded to 8-byte alignment, and followed by zero or more create contexts. Lease contexts request file or directory leases; durable contexts support both legacy durable handles and SMB3 persistent handle v2 reconnect/create GUIDs; POSIX contexts carry mode; security descriptor contexts encode mode/owner through special SIDs; query-id contexts request stable inode identifiers; EA contexts are spliced from caller-provided vectors. Create response parsing validates context bounds before extracting lease state, disk id, or POSIX owner/group/mode data.

Asynchronous reads and writes integrate with netfs subrequests. They choose channels, build request PDUs, request or adjust credits based on I/O size, optionally set SMB Direct channel descriptors and memory registrations, and call `cifs_call_async()`. Completion callbacks release credits, deregister RDMA memory, verify signatures for signed unencrypted reads, update stats and task I/O counters, set netfs retry/progress/EOF flags, and terminate subrequests. Synchronous read/write variants share the same PDU fields but use `cifs_send_recv()`.

Directory querying validates output offsets and lengths, parses entry chains defensively through `num_entries()`, accounts for SMB POSIX directory entries with variable owner/group SID and name tails, transfers ownership of response buffers into `cifs_search_info`, and handles `STATUS_NO_MORE_FILES` as end-of-search.

## State And Synchronization
The file coordinates with session and server locks in reconnect paths (`session_mutex`, `ses_lock`, `chan_lock`, `srv_lock`, `cifs_tcp_ses_lock`, and reconnect mutexes), with per-tcon counters and flags for remote opens, reconnect, and persistent handle reopen, and with netfs subrequest flags for I/O progress and retry. Request buffers have strict ownership rules: init helpers allocate, free helpers release, and error paths must avoid double-freeing response buffers that are handed to callers.

## Cross-File Interactions
This file is the concrete SMB2/SMB3 implementation behind function pointers installed by dialect tables in `smb2ops.c` and related global value tables. It depends on `smb2transport.c` for MID setup, signing, verification, key derivation, and AEAD allocation; on `connect.c` for session/tree/reconnect primitives and channel selection; on `file.c` for async read/write callers and handle lifetime; on `dir.c`/`inode.c`/`readdir.c` for path, metadata, and directory operations; on `smbdirect.c` for RDMA transport and memory registration; and on `compress.c` for write compression eligibility.

## Risks
The highest-risk areas are replay/reconnect behavior around handle-based requests, multichannel channel-key and reconnect ordering, create-context length/alignment handling, persistent-handle reconnect semantics, async read/write credit accounting, RDMA memory-registration lifetime, encryption/signing interaction, and parsing server-controlled variable-length contexts or directory entries. Many paths differ by dialect, server capabilities, mount flags, POSIX extensions, DFS, SMB Direct, encryption, compression, and fscache/netfs behavior, so regressions can be highly configuration-specific.
