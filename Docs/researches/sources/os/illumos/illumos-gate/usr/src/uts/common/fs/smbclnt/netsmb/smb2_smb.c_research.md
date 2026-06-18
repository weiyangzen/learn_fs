# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb2_smb.c

## Purpose

`smb2_smb.c` implements the main SMB2/3 protocol operations used by the illumos SMB client: negotiate, session setup, logoff, tree connect/disconnect, create/open, close, ioctl, read, write, and echo.

## Main Interfaces

Exported operations include `smb2_parse_smb1nego_resp()`, `smb2_smb_negotiate()`, `smb2_smb_ssnsetup()`, `smb2_smb_logoff()`, `smb2_smb_treeconnect()`, `smb2_smb_treedisconnect()`, `smb2_smb_ntcreate()`, `smb2_smb_close()`, `smb2_smb_ioctl()`, `smb2_smb_read()`, `smb2_smb_write()`, and `smb2_smb_echo()`.

The file also defines the supported dialect list, client capabilities, session-setup credit request count, and tunable timeouts for default, logon, open, read, write, append, and notice operations.

## Negotiation And Session Setup

`smb2_parse_smb1nego_resp()` handles the transitional SMB1 negotiate request that receives an SMB2 response, validates dialect `SMB2_DIALECT_02ff`, maps it back to the internal SMB1 marker, and adjusts SMB2 message ID state.

`smb2_smb_negotiate()` builds the SMB2 negotiate request, advertises dialects up to `vc_maxver`, optionally emits SMB 3.1.1 negotiate contexts, and parses server security mode, dialect, GUID, capabilities, max transact/read/write, security blob, and negotiate contexts. It initializes preauth hashing for SMB3.1.1, updates the preauth hash after the negotiate response, selects default AES-CCM for SMB3.0/3.0.2, initializes encryption mechanisms when possible, decides whether signing is required, backfills legacy SMB1 capability fields, validates minimum buffer sizes, and stores read/write/transaction maxima.

`smb2_smb_ssnsetup()` sends authentication blobs between kernel and user-space authentication state. It asks for credits, saves the session ID after the first response, handles `NT_STATUS_MORE_PROCESSING_REQUIRED` as `EINPROGRESS`, updates the SMB3.1.1 preauth hash during multi-step authentication, enables signing once SMB3.1.1 authentication completes, copies response security blobs to user memory, records final session flags, and rejects servers requiring encryption when the client failed to enable it.

## Tree And File Operations

`smb2_smb_treeconnect()` builds a UNC path, sends a VC-level tree connect, parses share type, share flags, share capabilities, max access, verifies required encryption support, maps SMB2 share type/capabilities to legacy share fields, and marks the share connected with the returned tree ID.

`smb2_smb_treedisconnect()` sends a short non-reconnecting disconnect with no-interrupt send semantics and clears the tree ID regardless of result. `smb2_smb_logoff()` sends a short non-reconnecting logoff when a session exists.

`smb2_smb_ntcreate()` builds an SMB2 CREATE request, skips a leading backslash in names for SMB2 semantics, optionally sends create contexts, pads the empty-variable-data case to the documented structure size, uses no-interrupt receive to avoid leaking opened FIDs, parses create action, timestamps, allocation size, EOF, attributes, file ID, and optional returned create contexts.

`smb2_smb_close()` sends a CLOSE for a persistent/volatile SMB2 file ID and uses no-interrupt send plus no reconnect to avoid racing teardown.

## Data And Control I/O

`smb2_smb_ioctl()` sends FSCTL-style SMB2 IOCTLs with optional input mblk data, receives output offset/length, always updates the caller's output size, and can return the output as an mdchain backed by an mblk.

`smb2_smb_read()` sends SMB2 READ using the uio offset and requested length, validates response structure and data offset, clamps an overlarge server-reported data length to the requested length, and moves data into the caller's `uio`.

`smb2_smb_write()` sends SMB2 WRITE with uio data and returns the server-reported written byte count. `smb2_smb_echo()` sends an internal no-reconnect ECHO request for the IOD path.

## Dependencies

This file depends on `smb2_rq.c` request helpers, mbchain/mdchain encoding and decoding, SMB IOD behavior, SMB session/share structures, negotiate-context helpers, preauth hashing, KDF/signing/encryption initialization, NT status constants, Unicode path encoding helpers, and common SMB1-compatible fields still used by shared client code.

## Research Notes

This is the operation-level SMB2/3 protocol core. High-risk areas are offset/length validation for security blobs, negotiate contexts, create contexts, IOCTL buffers, and read data; preauth hash failure propagation; signing enablement timing; encryption-required policy checks; no-interrupt handling around operations that allocate server-side IDs; and the compatibility backfill from SMB2/3 state into legacy SMB fields.
