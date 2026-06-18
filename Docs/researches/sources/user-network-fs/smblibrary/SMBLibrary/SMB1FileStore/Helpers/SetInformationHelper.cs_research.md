<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/SetInformationHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/SetInformationHelper.cs

Purpose: Translates SMB1 set-information request DTOs into shared FSCC `FileInformation` operations for backend application.

Important APIs/types/functions: `ToFileInformation` supports basic timestamps/attributes, disposition/delete-pending, allocation size, and end-of-file size.

Control flow: A type-dispatch chain creates the corresponding shared information class and copies writable fields.

State and persistence behavior: Stateless; it returns new shared DTOs and preserves SMB1 set-time sentinel semantics through `SetFileTime` fields.

Dependencies and integration points: Used by SMB1 SET_PATH/SET_FILE information handling before calling the file-store implementation. Depends on SMB1 set DTOs and shared file information classes.

Risks and edge cases: Unsupported set classes throw `NotImplementedException`. Allocation-size comments note SMB1 inputs are byte lengths rather than cluster-aligned values, which backend implementations must interpret carefully.

Test signals: Tests should cover each supported set class, delete-pending boolean encoding, zero/sentinel set times, and allocation/end-of-file boundary values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/SetInformationHelper.cs -->
