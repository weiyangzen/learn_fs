# sources/user-network-fs/samba/source3/smbd/globals.h

## Purpose
`globals.h` is the central declaration and protocol-state header for source3 smbd. It declares process globals, shared context structures, SMB1/SMB2 request/connection structures, server-connection state, macros for SMB2 compound iovec access, and prototypes for cross-module smbd entry points.

## Important APIs, Types, And Functions
Global declarations include mangling state, security/connection context stacks, SMB encryption contexts, VFS backend list, sparse buffer, parent context, global memcache, and global SMBXSRV client. `struct fsp_singleton_cache` caches a single file-id to fsp lookup. `struct sec_ctx` and `struct conn_ctx` represent pushed security and current-user/connection contexts.

The header declares many smbd APIs: info/query/set functions, notify cancellation, SMBXSRV connection/client/tcon lifecycle functions, SMB2 request processors, deferred-open helpers, send oplock/lease breaks, SMB2 fake SMB1 request construction, credit/size verification, and request completion/error wrappers. The macros `smbd_server_connection_terminate`, `smbd_server_disconnect_client`, `smbd_smb2_request_error`, and `smbd_smb2_request_done` preserve call-site location.

The main types are `struct smbXsrv_connection`, `struct smbd_smb2_send_queue`, `struct smbd_smb2_request`, `struct smbd_server_connection`, `struct file_modified_state`, and `struct aio_extra`. `struct smbXsrv_connection` stores transport, ack, SMB1 negotiation/session/signing state, SMB2 credits, dialect/capability negotiation, preauth hash, active requests, signing/encryption state, and multi-channel bookkeeping. `struct smbd_smb2_request` stores current compound index, signing/encryption state, async subrequest pointers, session/tcon refs, input/output vectors, fake SMB1 request compatibility, and chained fsp state. `struct smbd_server_connection` stores per-process connection lists, open files, notify context, search handles, oplock counts, deferred open queue, pthread pool, and client pointer.

## Control Flow
The header itself has no control flow, but it defines the state transitions expected by implementation files: an SMBXSRV client owns one or more connections, each connection has transport and SMB dialect substate, SMB2 requests move through parser/dispatcher/processor/completion functions, and server connections own the in-memory lists used by files, notify, searches, oplocks, and deferred opens. The SMB2 iovec macros assume `current_idx` selects the active compound element and map transform/header/body/dynamic slots in fixed increments.

## State And Persistence
All declared structures are in-memory runtime state. Some fields mirror persistent or cluster-visible SMBXSRV tables managed elsewhere, such as tcon and open globals. The tmpname macros define naming conventions for temporary names (`.::TMPNAME:` and directory prefix) but do not create persistence themselves.

## Dependencies And Integration Points
`globals.h` integrates most smbd subsystems: SMB1/SMB2 protocol handlers, SMBXSRV global tables, notify, file lifecycle, searches, oplocks, DCE/RPC server context, pthread pools, authentication/security tokens, loadparm-driven features, and profiling. Changes here have broad compile and behavioral impact because implementation files include it for core structures and prototypes.

## Risks
Layout changes can break many modules and assumptions in SMB2 compound processing, async completion, and SMB1 compatibility. The iovec macros are index-sensitive and can corrupt parsing or replies if vector layout changes. Global extern declarations require single-definition discipline in `globals.c` and sibling files. State fields such as `compat_chain_fsp`, transport termination flags, credits, and signing/encryption booleans are security-sensitive.

## Test Signals
Tests should cover SMB2 compound request vector indexing, request error/done wrappers preserving location metadata, transport termination/disconnect paths, SMB2 credit accounting, fake SMB1 request construction, chained fsp removal, tcon/session lookup paths, notify cancellation declarations linking correctly, tmpname prefix predicates, and build coverage for SMB1 enabled/disabled configurations.
