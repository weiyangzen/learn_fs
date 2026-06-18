# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ucred.h

## Purpose
User credential export structure and helper macros for process credentials, privileges, audit data, and labels.

## Main Interfaces
- Defines `struct ucred_s` with total size and offsets to embedded credential, privilege, audit, and label records.
- Defines accessor macros `UCCRED`, `UCPRIV`, `UCAUD`, and `UCLABEL`.
- Defines `UCREDSYS_UCREDGET` and `UCREDSYS_GETPEERUCRED` syscall subcommands.
- Defines kernel/user size macros for serialized `ucred` payloads.
- Declares `ucredminsize`, `pgetucred`, `get_audit_ucrsize`, and `_ucred_alloc`.

## Dependencies And Relationships
Includes process credential, privilege, TSOL label, and audit headers. Used by `getpeerucred`, procfs-style exported credentials, and local transport credential reporting.

## Research Notes
The structure is an offset-based packed export format. Consumers should use access macros rather than assuming fixed embedded offsets.
