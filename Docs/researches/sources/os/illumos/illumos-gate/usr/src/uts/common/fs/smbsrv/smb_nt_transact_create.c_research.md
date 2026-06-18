# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_create.c

## Summary
Implements SMB1 `NT_TRANSACT_CREATE`, a create/open variant that can carry extended attributes or a security descriptor. Extended attributes are not decoded, while an optional security descriptor is decoded and passed into the common open path.

## Main Responsibilities
- Decodes NT transact create parameters and pathname.
- Converts create flags to requested oplock level.
- Decodes optional self-relative security descriptors from request data.
- Frees decoded security descriptor memory after dispatch.
- Performs the same create-option validation and common-open flow as `NT_CREATE_ANDX`.
- Encodes normal or extended NT transact create response parameters.

## Key APIs
- `smb_pre_nt_transact_create()`.
- `smb_post_nt_transact_create()`.
- `smb_nt_transact_create()`.

## Important Behavior
The pre-handler decodes `sd_len` and, when nonzero, calls `smb_decode_sd()` over the request data mbuf, stores a kmem-allocated `smb_sd_t` on `op->sd`, and leaves cleanup to the post-handler.

The main create handler rejects unsupported file-id opens, invalid create options/dispositions, and delete-on-close without delete access. It maps backup intent to privileged credentials and delegates creation to `smb_common_open()`.

Responses are written to `xa->rep_param_mb`; extended responses include volume GUID space, file id, max access, and guest access fields.

## Dependencies
Shares the same open machinery as `smb_nt_create_andx.c`, plus security descriptor decode/free helpers from `smb_nt_transact_security.c`.

## Risks
The file comment says EAs are unsupported and not decoded. Clients sending non-empty EAs through this path do not get full EA application semantics.

Security descriptor ownership is split between decode, `op->sd`, and post-cleanup; early errors after allocation must keep cleanup paths intact.
