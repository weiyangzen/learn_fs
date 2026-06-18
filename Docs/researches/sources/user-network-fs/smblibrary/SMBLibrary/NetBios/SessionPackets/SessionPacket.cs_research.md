<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionPacket.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionPacket.cs

## Purpose
Base class and factory for RFC 1002 NetBIOS session packets and Direct TCP transport packet framing.

## Important APIs, Types, And Functions
Declarations: `public abstract class SessionPacket`. Constants: `public const int HeaderLength = 4;`; `public const int MaxSessionPacketLength = 131075;`; `public const int MaxDirectTcpPacketLength = 16777215;`. Important fields include `public SessionPacketTypeName Type`, `public byte[] Trailer`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods. Specific behavior: it parses the 4-byte type/length header, supports 17-bit NBT and 24-bit Direct TCP lengths, and dispatches by SessionPacketTypeName.

## Control Flow
The base constructor reads the session type and trailer length, the factory switches on type to instantiate concrete packet classes, and `GetBytes` rewrites the four-byte header from the current trailer length.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SessionPacketTypeName`, concrete session packet classes, `NetBiosUtils`, `System.IO`, and optionally `ArrayPool<byte>`. It integrates with SMB over NetBIOS/TCP and Direct TCP receive/send framing.

## Risks
Session packet lengths are trusted after the four-byte header; callers must ensure the receive buffer is large enough for Direct TCP lengths or increase it deliberately.

## Test Signals
Useful signals are fragmented TCP receive tests, multiple packets in one buffer, partial following-packet compaction, keep-alive/positive/negative/request/retarget/message factory dispatch, Direct TCP large-length framing, and Dispose/ArrayPool behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionPacket.cs -->
