# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileAttributes.java

## Purpose
Adapts SMB FileAllInformation into Java BasicFileAttributes time, type, and size values.

## Important APIs / Types / Functions
Defines class `SmbFileAttributes` in package `com.hierynomus.smbfs`. Important methods/functions include `SmbFileAttributes`, `lastModifiedTime`, `lastAccessTime`, `creationTime`, `isRegularFile`, `isDirectory`, `isSymbolicLink`, `isOther`, `size`, `fileKey`. Important fields include `fileInformation`. Source size: 78 lines.

## Control Flow
Control flow adapts Java NIO calls onto SMBJ objects: shares are opened from SMBClient connections, file attributes are read from FileAllInformation, streams expose list iteration, and channels guard shared position updates with a lock.

## State and Persistence
State fields observed: fileInformation. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.msfscc.fileinformation.FileAllInformation, com.hierynomus.smbfs.FileTimes.fromSmb. JDK/JCE dependencies: java.nio.file.attribute.BasicFileAttributes, java.nio.file.attribute.FileTime.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use mocked SMBJ DiskShare/File/Connection objects for close and position behavior plus integration tests against a disposable SMB share.
