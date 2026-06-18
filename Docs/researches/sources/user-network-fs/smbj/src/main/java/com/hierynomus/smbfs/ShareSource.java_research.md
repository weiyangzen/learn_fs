# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/ShareSource.java

## Purpose
Internal abstraction for opening named DiskShare instances and closing the holder that owns related network resources.

## Important APIs / Types / Functions
Defines interface `ShareSource` in package `com.hierynomus.smbfs`. Important methods/functions include `open`. Source size: 31 lines.

## Control Flow
Control flow adapts Java NIO calls onto SMBJ objects: shares are opened from SMBClient connections, file attributes are read from FileAllInformation, streams expose list iteration, and channels guard shared position updates with a lock.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Network/file resources are external integration state and require close-path coverage. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.smbj.share.DiskShare. JDK/JCE dependencies: java.io.Closeable, java.io.IOException.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use mocked SMBJ DiskShare/File/Connection objects for close and position behavior plus integration tests against a disposable SMB share.
