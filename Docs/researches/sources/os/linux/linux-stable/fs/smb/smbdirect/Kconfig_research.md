# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/Kconfig

## Summary
Defines the `SMBDIRECT` kernel config option for common SMB Direct support.

## Main Responsibilities
- Provide a tristate option defaulting to disabled.
- Require InfiniBand core and address translation support.
- Restrict builds so SMB Direct can be modular when InfiniBand is modular, or built-in when InfiniBand is built-in.
- Select `SG_POOL`.

## Cross-File Interactions
Controls building the common `fs/smb/smbdirect` module used by SMB Direct client/server transport adapters.

## Risks
Dependency mistakes can produce invalid built-in/module combinations for RDMA SMB Direct support.
