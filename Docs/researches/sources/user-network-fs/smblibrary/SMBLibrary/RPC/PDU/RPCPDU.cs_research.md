<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/RPCPDU.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/RPCPDU.cs

## Purpose
Base class and factory for connection-oriented DCE/RPC PDUs.

## Important APIs, Types, And Functions
Declarations: `public abstract class RPCPDU`. Constants: `public const int CommonFieldsLength = 16;`. Important fields include `public byte VersionMajor`, `public byte VersionMinor`, `public PacketFlags Flags`, `public DataRepresentationFormat DataRepresentation`, `public ushort AuthLength`, `public uint CallID`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods. Specific behavior: it parses common header fields, writes fragment/auth lengths, and dispatches concrete PDU types.

## Control Flow
Common parsing reads version, packet type, flags, data representation, fragment length, auth length, and call id. Static dispatch examines packet type and returns bind, bind-ack, bind-nak, request, response, or fault subclasses. Common writing updates fragment/auth lengths before subclass body serialization.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, RPC enums, `DataRepresentationFormat`, bind/result/context structures, syntax ids, and NDR payload producers/consumers. It integrates with connection-oriented MS-RPCE over SMB named pipes or TCP transports.

## Risks
Fragment length, auth length, and body offset math are trusted; malformed PDUs can produce negative or out-of-range data lengths if not prevalidated. Only little-endian NDR/common-field use is implemented in practice; unusual data representations are recorded but not generally used to switch reader endianness.

## Test Signals
Useful signals are bind/bind-ack/bind-nak/request/response/fault byte fixtures, first/last fragment flags, auth verifier lengths, context/result lists, object UUID request variants, fault status values, and rejection/versions-supported payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/RPCPDU.cs -->
