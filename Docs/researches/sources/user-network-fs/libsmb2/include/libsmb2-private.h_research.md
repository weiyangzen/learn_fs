# sources/user-network-fs/libsmb2/include/libsmb2-private.h

## Purpose
`libsmb2-private.h` is the central internal header for libsmb2. It defines the private context/PDU structures, receive-state machine, queue and vector bookkeeping, crypto/session fields, and internal packer/unpacker function contracts.

## Important APIs, Types, and Functions
Core types include `struct smb2_context`, `struct smb2_pdu`, `struct smb2_header`, `struct smb2_io_vectors`, `struct smb2dir`, `struct smb2_dirent_internal`, and `struct sync_cb_data`. Constants cover SMB2 header sizes, signature/key sizes, vector limits, tree nesting, credits, salts, and padding. Internal functions include allocation helpers, iovec management, tree-id stack management, PDU allocation/queue lookup/free, header decode, signature calculation, scalar endian get/set helpers, command-specific fixed/variable payload processors, file/filesystem/security descriptor encode/decode helpers, socket read/write helpers, timeout handling, and DCERPC alignment/scalar helpers.

## Control Flow
Incoming data advances through `enum smb2_recv_state`: SPL length, SMB2 or transform header, fixed payload, variable payload, padding, encrypted transform payload, or unknown cancelled-PDU data. Outgoing commands are built as `smb2_pdu` objects with header/iovec arrays and moved through `outqueue` and `waitqueue`. Each received header is matched to a waiting PDU by message id, decoded through command-specific fixed and variable processors, and completed through the PDU callback.

## State and Persistence Behavior
`struct smb2_context` owns socket descriptors, connection attempts, authentication settings, credentials, credits, tree/session/message ids, session/signing/sealing keys, encryption buffers, queues, receive buffers, last file id for related compounds, server capability values, error state, event callbacks, DCERPC settings, and server-list linkage. This is in-memory session state only; sensitive key material persists in the context until close/destroy.

## Dependencies and Integration Points
It includes Kerberos/GSSAPI headers only when `HAVE_LIBKRB5` is defined, and depends on public SMB2/DCERPC types from other headers. It is consumed by almost every implementation file under `lib/` and bridges public APIs, raw command packers, socket I/O, signing/encryption, and optional server mode.

## Risks and Edge Cases
The context is large and highly stateful; queue ownership, callback destruction, timeout processing, and encrypted/cancelled PDU handling are correctness-critical. `SMB2_MAX_PDU_SIZE` is 16 MiB and `SMB2_MAX_VECTORS` is fixed at 256, so compound or passthrough use must respect bounds. Sensitive keys require reliable cleanup paths.

## Test Signals
Exercise async request cancellation, compound requests, SMB3 encryption, signing verification, tree-id nesting, timeout expiry, partial socket reads/writes, out-of-order replies, server-side request decoding, and error string/NT status propagation.
