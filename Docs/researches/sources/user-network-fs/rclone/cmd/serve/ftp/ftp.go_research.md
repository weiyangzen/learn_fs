# sources/user-network-fs/rclone/cmd/serve/ftp/ftp.go

## Purpose

`ftp.go` implements `rclone serve ftp`, adapting rclone VFS operations to the `goftp.io/server/v2` driver and authentication interfaces.

## Important APIs, Types, and Functions

Configuration lives in `OptionsInfo`, `Options`, `Opt`, `AddFlags`, and Cobra `Command`. The `driver` type implements server lifecycle, authentication, VFS lookup, FTP filesystem operations, and logging. Key methods include `newServer`, `Serve`, `Shutdown`, `Addr`, `CheckPasswd`, `getVFS`, `Stat`, `ChangeDir`, `ListDir`, `DeleteDir`, `DeleteFile`, `Rename`, `MakeDir`, `GetFile`, and `PutFile`. `FileInfo` supplies owner/group/mode/modtime.

## Control Flow

Command or RC setup creates either a global VFS or an auth-proxy-backed per-user VFS. The FTP server parses listen address and passive port range, configures TLS if a key is set, and delegates operations to VFS. Reads open VFS files and seek offsets; writes either replace/create or append/overwrite from an offset.

## State and Persistence Behavior

State is in memory: global VFS, proxy object, cached obscured passwords by user, TLS flag, and server instance. FTP writes mutate the served remote through VFS.

## Dependencies and Integration Points

It integrates Cobra, RC, VFS flags, proxy auth, goftp server interfaces, rclone accounting/logging, obscure password storage, and filesystem user/group lookup.

## Risks and Test Signals

Risks include plain FTP exposure, passive-port misconfiguration, offset upload semantics, password cache lifetime, TLS requiring both cert/key, `Addr` synthesis not reflecting a dynamic `:0` listener, and global `proxy.Opt` use. Tests run generic FTP backend serve tests and RC creation on supported platforms.
