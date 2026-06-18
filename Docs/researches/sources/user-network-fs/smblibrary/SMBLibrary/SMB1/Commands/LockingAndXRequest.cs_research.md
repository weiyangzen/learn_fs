<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LockingAndXRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LockingAndXRequest.cs

## Purpose
Defines `LockingRange` for SMBLibrary protocol serialization.

## Important APIs, Types, And Functions
Declarations: `public class LockingRange`; `public class LockingAndXRequest : SMBAndXCommand`. Constants: `public const int Length32 = 10;`; `public const int Length64 = 20;`; `public const int ParametersLength = 12;`. Important fields include `public ushort PID`, `public ulong ByteOffset`, `public ulong LengthInBytes`, `public ushort FID`, `public LockType TypeOfLock`, `public byte NewOpLockLevel`, `public uint Timeout`. `CommandName` returns `SMB_COM_LOCKING_ANDX`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

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
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LockingAndXRequest.cs -->
