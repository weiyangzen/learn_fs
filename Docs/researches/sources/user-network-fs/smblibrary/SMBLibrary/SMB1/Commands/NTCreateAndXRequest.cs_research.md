<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCreateAndXRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCreateAndXRequest.cs

## Purpose
SMB_COM_NT_CREATE_ANDX request for opening or creating files with NT access masks, create disposition/options, impersonation, security flags, and path.

## Important APIs, Types, And Functions
Declarations: `public class NTCreateAndXRequest : SMBAndXCommand`. Constants: `public const int ParametersLength = 48;`. Important fields include `public byte Reserved`, `public NTCreateFlags Flags`, `public uint RootDirectoryFID`, `public AccessMask DesiredAccess`, `public long AllocationSize`, `public ExtendedFileAttributes ExtFileAttributes`, `public ShareAccess ShareAccess`, `public CreateDisposition CreateDisposition`, `public CreateOptions CreateOptions`, `public ImpersonationLevel ImpersonationLevel`. `CommandName` returns `SMB_COM_NT_CREATE_ANDX`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Extended variants share command names and are selected by length/WordCount, making regression tests for both classic and extended forms important.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCreateAndXRequest.cs -->
