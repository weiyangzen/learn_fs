<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/ResponsePDU.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/ResponsePDU.cs

## Purpose
Represents the connection-oriented DCE/RPC `ResponsePDU` PDU variant, including common header fields plus variant-specific body data.

## Important APIs, Types, And Functions
Declarations: `public class ResponsePDU : RPCPDU`. Constants: `public const int ResponseFieldsLength = 8;`. Important fields include `public uint AllocationHint`, `public ushort ContextID`, `public byte CancelCount`, `public byte Reserved`, `public byte[] Data`, `public byte[] AuthVerifier`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The constructor parses common RPC fields first, advances to the variant body, reads fixed fields and variable payloads, and leaves authentication bytes in `AuthVerifier` when present. `GetBytes` sets `AuthLength`, allocates `Length`, writes common fields, then emits variant fields and payloads.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, RPC enums, `DataRepresentationFormat`, bind/result/context structures, syntax ids, and NDR payload producers/consumers. It integrates with connection-oriented MS-RPCE over SMB named pipes or TCP transports.

## Risks
Fragment length, auth length, and body offset math are trusted; malformed PDUs can produce negative or out-of-range data lengths if not prevalidated. Only little-endian NDR/common-field use is implemented in practice; unusual data representations are recorded but not generally used to switch reader endianness.

## Test Signals
Useful signals are bind/bind-ack/bind-nak/request/response/fault byte fixtures, first/last fragment flags, auth verifier lengths, context/result lists, object UUID request variants, fault status values, and rejection/versions-supported payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/ResponsePDU.cs -->
