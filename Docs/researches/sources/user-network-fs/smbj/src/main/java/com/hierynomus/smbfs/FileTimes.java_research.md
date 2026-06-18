# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/FileTimes.java

## Purpose
Small conversion helper from SMB/MS-DTYP FileTime to java.nio.file.attribute.FileTime.

## Important APIs / Types / Functions
Defines class `FileTimes` in package `com.hierynomus.smbfs`. Important methods/functions include `FileTimes`, `fromSmb`. Source size: 27 lines.

## Control Flow
Control flow adapts Java NIO calls onto SMBJ objects: shares are opened from SMBClient connections, file attributes are read from FileAllInformation, streams expose list iteration, and channels guard shared position updates with a lock.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.nio.file.attribute.FileTime.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use mocked SMBJ DiskShare/File/Connection objects for close and position behavior plus integration tests against a disposable SMB share.
