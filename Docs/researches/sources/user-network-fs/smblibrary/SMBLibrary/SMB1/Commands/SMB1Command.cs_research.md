<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SMB1Command.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SMB1Command.cs

## Purpose
Abstract base and parser dispatch for SMB1 command payloads.

## Important APIs, Types, And Functions
Declarations: `public abstract class SMB1Command`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods. Specific behavior: it owns WordCount/SMBParameters/ByteCount/SMBData framing, request/response factories, and known WordCount quirks.

## Control Flow
The base constructor reads WordCount, SMBParameters, ByteCount, and SMBData. `GetBytes` validates an even parameter length, computes WordCount and ByteCount, handles the NT_CREATE_ANDX extended declared WordCount exception, and writes the framed command body. Static request/response dispatch switches on `CommandName` and WordCount to choose concrete command classes or `ErrorResponse`.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Dispatch falls back to `ErrorResponse` for unrecognized WordCount variants, so adding new command variants requires updating both request and response factories.

## Test Signals
Useful signals are request/response factory tests for every supported command, classic versus extended WordCount variants, error-status fallback, even parameter length validation, and NT_CREATE_ANDX declared WordCount handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SMB1Command.cs -->
