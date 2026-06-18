<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/QueryInfoHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/QueryInfoHelper.cs

## Purpose
SMB2 query-info handling for file, file-system, and security information. It validates handles and access, delegates to file-store query APIs, maps unsupported levels to SMB statuses, and trims or errors on oversized output.

## APIs, Types, and Functions
`QueryInfoHelper.GetQueryInfoResponse()` branches by `InfoType.File`, `FileSystem`, or `Security`. It uses `GetFileInformation()`, `GetFileSystemInformation()`, `GetSecurityInformation()`, `QueryInfoResponse` setters, and `ErrorResponse`.

## Control Flow, State, and Persistence
File and security queries require an open file object; file-system queries use the share root. File-system shares are checked for read access. File information catches `UnsupportedInformationLevelException` as `STATUS_INVALID_INFO_CLASS` and `NotImplementedException` as `STATUS_NOT_IMPLEMENTED`. File/file-system output larger than the client buffer is truncated with `STATUS_BUFFER_OVERFLOW`; security output larger than the buffer returns `STATUS_BUFFER_TOO_SMALL` with required size data.

## Dependencies and Integration
Called by SMB2 dispatch. It depends on SMB information-class parsers, security descriptor classes, `ByteReader`, `LittleEndianConverter`, and `FileSystemShare` access policy.

## Risks and Test Signals
Risks include inconsistent overflow behavior between info types, path-based access checks separate from actual handle access, and store exceptions beyond the caught types propagating. Test supported and unsupported info classes, access denial, security descriptor size errors, truncation, named-pipe query behavior, and invalid file IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/QueryInfoHelper.cs -->
