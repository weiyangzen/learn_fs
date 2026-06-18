# File Research: sources/windows/winfsp/src/dll/library.h

This is the shared internal header for the WinFsp DLL.

Key contents:
- Enables `WINFSP_DLL_INTERNAL` and includes public WinFsp headers, launcher API, minimal runtime support, `strsafe`, and configuration.
- Defines `LIBRARY_NAME`, debug logging/test macros, and finalize/register function declarations.
- Declares subsystem helpers for SxS suffixing, well-known SIDs, Mount Manager calls, LDAP calls, diagnostics, directory creation, module version/path lookup, adaptive locks, directory buffer peeking, service stop/control handling.
- Provides path helpers:
  - `FspPathSuffixIndex`
  - `FspPathIsDrive`
  - `FspPathIsMountmgrMountPoint`
  - `FspPathIsMountmgrDrive`
- Defines `FSP_NEXT_EA` for EA walking.

Filesystem relevance:
- Central declaration surface for the DLL implementation files in this group.
- The mount path helpers are used directly by `mount.c` and network/mount workflows.
