# sources/sync-backup/unison/src/osxsupport.c

Purpose: macOS-specific OCaml C stubs for Finder info and resource fork metadata.

Important APIs: `isMacOSX`, `getFileInfos(path, need_size)`, and `setFileInfos(path, fInfo)`.

Control flow: on Apple platforms, `getFileInfos` calls `getattrlist` for `ATTR_CMN_FNDRINFO` and optionally `ATTR_FILE_RSRCLENGTH`, validates returned buffer length, and returns a pair of 32-byte Finder info string and int64 resource fork length. `setFileInfos` calls `setattrlist`; on `EACCES`, it temporarily adds owner-write permission, retries, and restores the original mode.

State/persistence: reads and writes macOS Finder metadata and may briefly chmod read-only files while setting metadata.

Dependencies/integration: Apple `getattrlist`/`setattrlist`, OCaml Unix error mapping, and higher-level Unison property synchronization.

Risks: temporary chmod has failure windows if restoration fails or another process observes the mode. Non-Apple builds raise `ENOSYS`. Buffer-size validation is strict and can fail if OS API shape changes.

Test signals: macOS tests should verify Finder info/resource fork size roundtrip, read-only file metadata updates, and `ENOSYS` behavior on non-macOS.
