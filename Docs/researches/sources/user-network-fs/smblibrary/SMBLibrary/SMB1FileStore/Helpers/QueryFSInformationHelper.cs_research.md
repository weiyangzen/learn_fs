<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/QueryFSInformationHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/QueryFSInformationHelper.cs

Purpose: Converts SMB1 file-system query levels to shared FSCC file-system information classes and converts shared responses back to SMB1 query structures.

Important APIs/types/functions: `ToFileSystemInformationClass` supports volume, size, device, and attribute levels; `FromFileSystemInformation` creates `QueryFSVolumeInfo`, `QueryFSSizeInfo`, `QueryFSDeviceInfo`, or `QueryFSAttibuteInfo`.

Control flow: The helper performs a straight switch for request level translation and an `is` chain for response DTO conversion.

State and persistence behavior: Stateless; it copies volume labels, serials, allocation unit counts, device metadata, and file-system attributes into new SMB1 objects.

Dependencies and integration points: Integrates SMB1 TRANS2 query FS handling with shared `FileSystemInformation` classes and the concrete SMB1 query FS serializers.

Risks and edge cases: Unknown levels and subclasses fail fast. The attribute class name is misspelled as `QueryFSAttibuteInfo`, so callers must use the existing type name consistently.

Test signals: Tests should cover all four conversions, Unicode file-system names, and failure behavior for unsupported information classes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/QueryFSInformationHelper.cs -->
