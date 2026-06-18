# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileChannel.java

## Purpose
SeekableByteChannel adapter over an SMBJ File with locked position tracking, read/write/truncate, and idempotent close.

## Important APIs / Types / Functions
Defines class `SmbFileChannel` in package `com.hierynomus.smbfs`. Important methods/functions include `SmbFileChannel`, `read`, `write`, `position`, `size`, `truncate`, `isOpen`, `close`. Important fields include `lock`, `holder`, `file`, `position`, `closed`. Source size: 121 lines.

## Control Flow
Control flow adapts Java NIO calls onto SMBJ objects: shares are opened from SMBClient connections, file attributes are read from FileAllInformation, streams expose list iteration, and channels guard shared position updates with a lock.

## State and Persistence
State fields observed: lock, holder, file, position, closed. Concurrency state is explicit and lives only in process memory. Network/file resources are external integration state and require close-path coverage. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.smbj.share.File. JDK/JCE dependencies: java.io.IOException, java.nio.ByteBuffer, java.nio.channels.SeekableByteChannel, java.util.concurrent.atomic.AtomicBoolean, java.util.concurrent.locks.ReentrantLock.

## Risks and Edge Cases
concurrency semantics need tests for timeout, cancellation, interruption, and double-close paths.

## Test Signals
Use mocked SMBJ DiskShare/File/Connection objects for close and position behavior plus integration tests against a disposable SMB share.
