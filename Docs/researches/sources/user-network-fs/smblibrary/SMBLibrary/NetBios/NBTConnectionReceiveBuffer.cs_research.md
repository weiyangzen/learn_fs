<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NBTConnectionReceiveBuffer.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NBTConnectionReceiveBuffer.cs

## Purpose
Buffers TCP NetBIOS session bytes until a complete session packet is available.

## Important APIs, Types, And Functions
Declarations: `public class NBTConnectionReceiveBuffer : IDisposable`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it uses a rented or allocated byte array, cached packet length, compaction, and SessionPacket factory dispatch.

## Control Flow
Callers receive into `Buffer` at `WriteOffset`, report bytes with `SetNumberOfBytesReceived`, poll `HasCompletePacket`, then dequeue either a parsed `SessionPacket` or raw packet bytes. Dequeue removes consumed bytes and compacts leftovers when a partial following packet remains.

## State And Persistence
Mutable state is the rented backing buffer, read offset, byte count, and cached packet length. It is explicitly not thread-safe. `Dispose` returns the rented buffer on modern target frameworks. There is no durable persistence; state only spans a TCP receive loop.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SessionPacketTypeName`, concrete session packet classes, `NetBiosUtils`, `System.IO`, and optionally `ArrayPool<byte>`. It integrates with SMB over NetBIOS/TCP and Direct TCP receive/send framing.

## Risks
Session packet lengths are trusted after the four-byte header; callers must ensure the receive buffer is large enough for Direct TCP lengths or increase it deliberately. The buffer is not thread-safe and cached `m_packetLength` assumes callers always call `HasCompletePacket` before dequeueing.

## Test Signals
Useful signals are fragmented TCP receive tests, multiple packets in one buffer, partial following-packet compaction, keep-alive/positive/negative/request/retarget/message factory dispatch, Direct TCP large-length framing, and Dispose/ArrayPool behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NBTConnectionReceiveBuffer.cs -->
