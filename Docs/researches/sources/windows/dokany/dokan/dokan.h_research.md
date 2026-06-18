# File Research: sources/windows/dokany/dokan/dokan.h

Primary public Dokan user-mode API header defining mount options, file operation callback contracts, lifecycle APIs, notifications, and helper functions.

Key responsibilities:
- Defines DLL import/export calling convention macros `DOKANAPI` and `DOKAN_CALLBACK`.
- Defines version constants, driver/network provider names, mount result codes, and exception codes.
- Defines `DOKAN_OPTIONS`, including version, threading mode, feature flags, global context, mount point, UNC name, timeout, sector/allocation sizing, and optional volume security descriptor.
- Defines `DOKAN_FILE_INFO`, the per-operation context passed to user callbacks.
- Defines callback typedefs `PFillFindData` and `PFillFindStreamData`.
- Defines `DOKAN_OPERATIONS`, the complete callback table for user filesystem implementations.
- Declares lifecycle APIs: `DokanInit`, `DokanShutdown`, `DokanMain`, `DokanCreateFileSystem`, wait APIs, close/unmount APIs.
- Declares mount point list APIs, wildcard matching, version queries, timeout reset, requestor token retrieval, create-flag mapping, Win32-to-NTSTATUS conversion, and change notification APIs.

Important behavior specified by the header:
- `ZwCreateFile` is central and must set `DOKAN_FILE_INFO.IsDirectory` for directories.
- User `Context` stored in `DOKAN_FILE_INFO.Context` is carried between related operations and must be cleaned by user code.
- `Cleanup` is where delete-on-close deletion must occur when `DeletePending` is true.
- `CloseFile` is final context cleanup and cannot report failure.
- Read/write callbacks may occur after cleanup for memory-mapped I/O.
- `FindFilesWithPattern` is preferred; `FindFiles` is fallback.
- Delete callbacks should validate whether deletion is allowed, not delete immediately.
- Volume information and disk free-space callbacks may occur without a preceding create.
- Alternate stream enumeration is only used with `DOKAN_OPTION_ALT_STREAM`.
- Notifications must be called independently of normal filesystem operation callbacks and require absolute mounted paths.

Dependencies:
- Includes Windows headers, `ntstatus.h`, `fileinfo.h`, and `public.h`.
- Public contracts rely on Windows file information classes, security descriptors, access masks, file attributes, and NTSTATUS values.

Notable risks:
- This is ABI/API surface: structure layout, callback order, and calling convention changes would break consumers.
- Many callback contracts require user filesystems to implement Windows semantics precisely, especially cleanup/delete, sharing, paging I/O, and directory state.
- `DOKAN_FILE_INFO` contains reserved fields that consumers must not modify, but the header cannot enforce that.
