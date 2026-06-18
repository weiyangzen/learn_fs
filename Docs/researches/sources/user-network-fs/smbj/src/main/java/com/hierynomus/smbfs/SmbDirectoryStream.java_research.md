# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbDirectoryStream.java

## Purpose
DirectoryStream implementation over a precomputed path list, enforcing one iterator and a closed state.

## Important APIs / Types / Functions
Defines class `SmbDirectoryStream` in package `com.hierynomus.smbfs`. Important methods/functions include `SmbDirectoryStream`, `iterator`, `close`. Important fields include `list`, `closed`, `iteratorTaken`. Source size: 51 lines.

## Control Flow
Control flow adapts Java NIO calls onto SMBJ objects: shares are opened from SMBClient connections, file attributes are read from FileAllInformation, streams expose list iteration, and channels guard shared position updates with a lock.

## State and Persistence
State fields observed: list, closed, iteratorTaken. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.io.IOException, java.nio.file.DirectoryStream, java.nio.file.Path, java.util.Iterator, java.util.List.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use mocked SMBJ DiskShare/File/Connection objects for close and position behavior plus integration tests against a disposable SMB share.
