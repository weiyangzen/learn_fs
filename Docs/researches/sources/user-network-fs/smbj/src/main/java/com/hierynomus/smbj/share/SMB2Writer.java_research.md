<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/SMB2Writer.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/SMB2Writer.java

Purpose: Generic writer for any Share entry addressed by SMB2FileId, used by regular files and printer shares.

Important APIs/types/functions: write(byte[], long), write(byte[], long, int, int), write(ByteChunkProvider), write(ByteChunkProvider, ProgressListener), writeAsync(byte[], long, int, int), writeAsync(ByteChunkProvider), and getOutputStream().

Control flow: Synchronous write loops while provider.isAvailable(), calls Share.write(), accumulates bytes written, and emits progress. Async write loops providers into Share.writeAsync futures, records the provider's last prepared write size, transforms each response to verify the server wrote the full chunk, then sequences and sums the futures.

State and persistence behavior: Holds Share, SMB2FileId, and entryName. Provider offset state is mutated as chunks are prepared/written. Remote entry contents are mutated.

Dependencies and integration points: Used by File and PrinterShare. Depends on ByteChunkProvider, ArrayByteChunkProvider, FileOutputStream, Futures transforms/sequence, SMB2WriteResponse, and ProgressListener.

Risks: Synchronous path does not validate short writes as strictly as async path. Async path queues all chunks immediately, which can create many outstanding requests for large providers. Progress uses provider.getOffset(), which must already reflect consumed bytes.

Test signals: Multi-chunk sync write, short-write async exception, async aggregate sum, progress counts/offsets, output stream creation with offset, and provider exception propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/SMB2Writer.java -->
