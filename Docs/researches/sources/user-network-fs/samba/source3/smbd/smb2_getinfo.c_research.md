# sources/user-network-fs/samba/source3/smbd/smb2_getinfo.c

Purpose: implements SMB2 GETINFO for file, filesystem, security, and quota information by bridging SMB2 queries into source3 query, VFS, security descriptor, and quota helpers.

Important APIs and types: `smbd_smb2_request_process_getinfo()` validates and decodes the request. `smbd_smb2_getinfo_send()` / `smbd_smb2_getinfo_recv()` wrap execution. `struct smbd_smb2_getinfo_state` stores output plus a call status that can be `STATUS_BUFFER_OVERFLOW` or another data-bearing status. `smb2_ipc_getinfo()` returns pipe `FILE_STANDARD_INFO`.

Control flow: the processor checks size `0x29`, input offset/length, max-trans limits, credit charge, and fsp resolution. File info enforces access for selected classes, maps SMB2 classes to passthrough/trans2 levels, gates POSIX and normalized-name classes, refreshes stat state, optionally reads share-mode delete-pending state, and calls `smbd_do_qfilepathinfo()`. Filesystem info calls `smbd_do_qfsinfo()`. Security info calls `smbd_do_query_security_desc()` and returns a 4-byte needed size on `BUFFER_TOO_SMALL`. Quota info is compiled under `HAVE_SYS_QUOTAS`, validates quota handles, NDR-pulls `smb2_query_quota_info`, rejects unsupported single-start-SID form, and calls quota query helpers. The done callback emits data-bearing errors or a normal `0x08` GETINFO response.

State and persistence: mostly read-only. It refreshes fsp stat data and reads share-mode/quota/security state. Output blobs are talloc-owned and moved to the SMB2 response.

Dependencies and integration: depends on trans2 query implementations, VFS stat/fstat, access checks, share-mode metadata, security descriptor helpers, generated quota/security NDR, fake SMB1 request glue, and negotiated max-transfer limits.

Risks: fixed-portion and output-length checks determine `INFO_LENGTH_MISMATCH` versus truncation. `INVALID_LEVEL` must map to `INVALID_INFO_CLASS` in some paths. POSIX info must be limited to POSIX opens. Security descriptor too-small responses intentionally carry data. Quota behavior differs by build configuration.

Test signals: cover file/filesystem/security/quota info, malformed input offsets, max-trans and credit failures, partial-buffer overflow, IPC pipe standard info, normalized-name dialect gating, POSIX info on non-POSIX handles, and quota SID-list parsing.
