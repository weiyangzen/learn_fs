# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileSystem.java

Purpose: `SmbFileSystem` adapts an SMB share to the Java NIO `FileSystem` contract. It owns the provider reference, a `ShareSource`, the share name, a root `SmbPath`, and an `open` flag.

Important APIs and control flow: path creation normalizes `/` to SMB backslashes and returns root, absolute, or relative `SmbPath` instances. Directory listing opens a `DiskShare`, calls `list`, filters `.` and `..`, applies the caller filter, and returns an `SmbDirectoryStream`. File operations translate NIO options into SMB access masks, create dispositions, and create options before opening `File` handles. Copy uses server-side `remoteCopyTo`; move opens with `FILE_WRITE_ATTRIBUTES` and renames; delete opens with `DELETE` and marks delete-on-close.

State, dependencies, and integration: every operation opens the configured share through `ShareSource`; channel lifetime is handed to `SmbFileChannel` with the share holder and SMB file. It depends on SMBJ share primitives, MS-SMB2 create/access enums, and NIO SPI types.

Risks: several NIO surfaces are unimplemented. `checkAccess` only supports existence checks, not modes. Option translation is partial, and same-share copy assumes source and destination are on one share holder. Test signals should cover path parsing, create/truncate/append modes, missing-file exception mapping, remote copy/move/delete, holder closing, and unsupported option behavior.
