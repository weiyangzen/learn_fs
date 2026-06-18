<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileAllInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileAllInfo.cs

Purpose: Concrete SMB1 query-file information payload for `SMB_QUERY_FILE_ALL_INFO`.

Important APIs/types/functions: `QueryFileAllInfo` exposes a buffer constructor, `GetBytes`, and `InformationLevel`; it carries combined basic, standard, EA, and name information with a variable UTF-16 name.

Control flow: Parsing reads the FSCC-like binary layout from a supplied offset. Serialization builds a fresh byte array, recomputing length fields and writing little-endian numeric values and UTF-16 strings where applicable.

State and persistence behavior: State is the in-memory DTO fields only. `QueryFileStreamInfo` owns a mutable `Entries` list and calculates padded serialized length from it.

Dependencies and integration points: Used by `QueryInformation.GetQueryInformation` and `QueryInformationHelper` for SMB1 query responses and conversions to shared file-store objects.

Risks and edge cases: Constructors trust declared lengths and offsets. Stream parsing depends on nonzero `NextEntryOffset` progress; string classes do not validate even byte counts. Boolean fields accept any nonzero byte as true.

Test signals: Tests should include parse/write round trips, empty and long UTF-16 names, stream alignment with multiple entries, compression reserved bytes, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileAllInfo.cs -->
