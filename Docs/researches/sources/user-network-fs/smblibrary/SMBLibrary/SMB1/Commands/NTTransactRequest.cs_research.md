<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactRequest.cs

## Purpose
Primary SMB_COM_NT_TRANSACT request with setup words and aligned transaction parameter/data blocks.

## Important APIs, Types, And Functions
Declarations: `public class NTTransactRequest : SMB1Command`. Constants: `public const int FixedSMBParametersLength = 38;`. Important fields include `public byte MaxSetupCount`, `public ushort Reserved1`, `public uint TotalParameterCount`, `public uint TotalDataCount`, `public uint MaxParameterCount`, `public uint MaxDataCount`, `public NTTransactSubcommandName Function`, `public byte[] Setup`, `public byte[] TransParameters`, `public byte[] TransData`. `CommandName` returns `SMB_COM_NT_TRANSACT`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Transaction parameter/data displacement and alignment bugs can corrupt multi-part transaction reconstruction.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactRequest.cs -->
