# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/FileByteChunkProvider.java

Purpose: `FileByteChunkProvider` streams bytes from a local file for SMB writes.

Important APIs and control flow: constructor opens a `FileInputStream`, wraps it in `InputStreamByteChunkProvider`, skips to the requested offset, and sets the remote file offset. All provider methods delegate to the underlying input-stream provider.

State, dependencies, and integration: owns the local `File`, opened stream through the delegate, and offset state.

Risks: `ensureSkipped` calls `fis.skip(offset)` each loop rather than the remaining amount, which can overshoot accounting or loop oddly. `available()` is not a reliable file length indicator. Tests should cover offset zero/nonzero, skip failure, close closes the stream, and large offsets.
