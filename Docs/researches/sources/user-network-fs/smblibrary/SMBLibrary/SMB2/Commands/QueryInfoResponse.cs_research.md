<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryInfoResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryInfoResponse.cs

Purpose: Implements the SMB2 QUERY_INFO response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `QueryInfoResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for output buffer offset/length and typed helper decoders; helpers parse file, filesystem, or security descriptor information.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryInfoResponse.cs -->
