<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateResponse.cs

## Purpose
Classic negotiate response with dialect index, security mode, limits, capabilities, server time, challenge, and optional domain/server strings.

## Important APIs, Types, And Functions
Declarations: `public class NegotiateResponse : SMB1Command`. Constants: `public const int ParametersLength = 34;`. Important fields include `public ushort DialectIndex`, `public SecurityMode SecurityMode`, `public ushort MaxMpxCount`, `public ushort MaxNumberVcs`, `public uint MaxBufferSize`, `public uint MaxRawSize`, `public uint SessionKey`, `public Capabilities Capabilities`, `public DateTime SystemTime`, `public short ServerTimeZone`. `CommandName` returns `SMB_COM_NEGOTIATE`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateResponse.cs -->
