<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/FindInformationHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/FindInformationHelper.cs

Purpose: Bridges SMB1 TRANS2 find information levels to the shared FSCC query-directory model and back to SMB1 wire structures.

Important APIs/types/functions: `ToFileInformationClass`, `ToFindInformationList`, and `ToFindInformation` map SMB1 `FindInformationLevel` values and `QueryDirectoryFileInformation` subclasses to concrete `FindInformation` records.

Control flow: Dispatch is type- and enum-based. `ToFindInformationList` walks query results until adding another serialized entry would exceed `maxLength`, preserving page boundaries for directory enumeration responses.

State and persistence behavior: No persistent state; it mutates only the returned list and per-entry DTO fields including timestamps, EA size, short name, file id, and attributes.

Dependencies and integration points: Depends on SMB1 find structures, shared `FileInformationClass` / query-directory classes, and `Utilities` byte helpers indirectly through serialized length calculations. It is used by SMB1 file-store query-directory response assembly.

Risks and edge cases: Unsupported levels throw `UnsupportedInformationLevelException`; unknown input subclasses throw `NotImplementedException`. Several mappings use last-write time as last-change/attribute-change time, which can lose fidelity when a backend exposes separate change time.

Test signals: Round-trip tests should cover every supported information level, max-length truncation at entry boundaries, Unicode and OEM length calculation, and preservation of file id / short-name fields for both ID and non-ID formats.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/FindInformationHelper.cs -->
