# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/ChangeNotifyIntegrationTest.java

Source read signal: reviewed complete local file (105 lines, 5523 bytes).

## Purpose
`ChangeNotifyIntegrationTest.java` covers SMB2 change notify integration tests. verifies directory watch notifications for file creation and cancellation of an outstanding notify request.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
The watch test opens a directory, issues recursive `watch()`, creates a file, waits for the future, and asserts `FILE_ACTION_ADDED` plus file name. The cancel test sends a watch with `send()`, cancels it, and expects an empty notify list.

## State and persistence
Uses transient files/directories in the `user` share and asynchronous futures.

## Dependencies and integration points
Depends on `DiskShare`, `Directory.watch`, SMB2 completion/cancel behavior, `FileNotifyAction`, and the Samba container.

## Risks
Timing can be flaky if creation races with watch registration or cancellation. Samba behavior for canceled notify responses is part of the contract.

## Test signals
Signals are prompt future completion with one notify item and successful cancel returning an empty response.
