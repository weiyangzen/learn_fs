# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/ShareSourceImpl.java

## Purpose
Opens SMB connections, authenticates sessions, connects disk shares, and closes share/session/connection holders for the NIO filesystem layer.

## Important APIs / Types / Functions
Defines class `ShareSourceImpl` in package `com.hierynomus.smbfs`. Important methods/functions include `ShareSourceImpl`, `open`, `close`, `HolderImpl`, `share`. Important fields include `client`, `host`, `port`, `context`, `closed`, `share`. Source size: 82 lines.

## Control Flow
Control flow adapts Java NIO calls onto SMBJ objects: shares are opened from SMBClient connections, file attributes are read from FileAllInformation, streams expose list iteration, and channels guard shared position updates with a lock.

## State and Persistence
State fields observed: client, host, port, context, closed, share. Concurrency state is explicit and lives only in process memory. Network/file resources are external integration state and require close-path coverage. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.smbj.SMBClient, com.hierynomus.smbj.auth.AuthenticationContext, com.hierynomus.smbj.connection.Connection, com.hierynomus.smbj.session.Session, com.hierynomus.smbj.share.DiskShare. JDK/JCE dependencies: java.io.IOException.

## Risks and Edge Cases
network timeouts, proxy parsing, and close behavior need integration tests.

## Test Signals
Use mocked SMBJ DiskShare/File/Connection objects for close and position behavior plus integration tests against a disposable SMB share.
