# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/FileByteChunkProviderSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/FileByteChunkProviderSpec.groovy

Purpose: validates file-backed chunk streaming. It creates temporary files with random bytes and checks full chunk output, partial chunk output, availability after the first chunk when data remains, and starting reads at a supplied file offset.

State and persistence: temporary filesystem files are created for test data; provider tracks file input position. Dependencies are Java `File`, random byte generation, output streams, and `ByteChunkProvider.CHUNK_SIZE`. Integration point is SMB upload/write from local files. Risks covered include file-offset seek behavior, partial final chunks, available-byte accounting, and stream cleanup. Test signal is useful but random inputs make failures less directly inspectable.
