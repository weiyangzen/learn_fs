<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/SetInfoHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/SetInfoHelper.cs

## Purpose
SMB2 set-info handling for file metadata, file-system metadata, and security descriptors. It parses client buffers into typed information objects, enforces write access, calls backing-store setters, and updates server-side open-file paths after renames.

## APIs, Types, and Functions
`SetInfoHelper.GetSetInfoResponse()` handles all branches. It uses `FileInformation.GetFileInformation()`, `FileSystemInformation.GetFileSystemInformation()`, `SecurityDescriptor`, `IFileStore.SetFileInformation()`, `SetFileSystemInformation()`, and `SetSecurityInformation()`.

## Control Flow, State, and Persistence
File/security operations require a valid open file. File-system operations check root write access. Unsupported information levels map to invalid-info-class or not-supported statuses; parse failures map to invalid-parameter. Rename requests get an extra write-access check on the target path and update `openFile.Path` after store success. Store mutations persist in the backing file store.

## Dependencies and Integration
Called by SMB2 dispatch. It depends on SMB information parsers, security descriptor parsing, `FileSystemShare` access events, and `INTFileStore` setter implementations.

## Risks and Test Signals
Risks include broad catch blocks hiding parse specifics, path-only authorization that may not match ACL semantics, rename target normalization issues, and possible bug-prone `SetSecurityInformation(openFile, ...)` call shape depending on file-store expectations. Test invalid buffers, unsupported classes, denied target rename, successful rename path update, security descriptor set, and file-system set failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/SetInfoHelper.cs -->
