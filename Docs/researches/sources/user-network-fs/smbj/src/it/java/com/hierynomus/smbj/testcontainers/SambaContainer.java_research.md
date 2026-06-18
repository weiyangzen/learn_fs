# sources/user-network-fs/smbj/src/it/java/com/hierynomus/smbj/testcontainers/SambaContainer.java

Source read signal: reviewed complete local file (180 lines, 7084 bytes).

## Purpose
`SambaContainer.java` covers Testcontainers Samba fixture. builds and runs the Samba image, exposes port 445, provides authenticated/connected SMB client helpers, URI helpers, container file operations, and debug logging setup.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
The singleton builds an image from `src/it/docker-image`, starts smbd/nmbd, waits for the port, then tests call wrappers that open `SMBClient`, `Connection`, and `Session` objects around callbacks.

## State and persistence
State includes one shared container, fixed host port 445 mapping, generated Docker image, share files, logs, and temporary files manipulated by tests.

## Dependencies and integration points
Depends on Testcontainers, Dockerfile builder, Logback, SMBJ client/session APIs, and `TestingUtils` credentials.

## Risks
Fixed exposed port 445 can conflict on developer/CI hosts. The Java builder's Alpine version can drift from the Dockerfile. Helper failures drop command output.

## Test signals
Signals are successful image build/start, SMB connection/auth helper success, and container file helper correctness.
