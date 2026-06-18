<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/ServerUI.cs -->
# sources/user-network-fs/smblibrary/SMBServer/ServerUI.cs

## Purpose
Code-behind for the sample SMB server UI. It loads local addresses, reads settings, constructs shares and authentication providers, starts/stops the SMB server and optional NetBIOS name server, and enforces simple share access policy.

## APIs, Types, and Functions
Important methods are constructor, `ServerUI_Load()`, `btnStart_Click()`, `btnStop_Click()`, `chkSMB1_CheckedChanged()`, `chkSMB2_CheckedChanged()`, `InitializeShare()`, `Contains()`, and `IndexOf()`.

## Control Flow, State, and Persistence
On load the IP combo is populated with `Any` plus IPv4 addresses. Start chooses transport, builds integrated or independent NTLM authentication, reads `Settings.xml`, creates `FileSystemShare` objects backed by `NTDirectoryFileSystem`, attaches synchronous logging, starts `SMBServer`, and optionally starts `NameServer` for NetBIOS over TCP. UI controls are disabled while running. Stop stops server/logging/name server and re-enables controls. Access policy maps wildcard `*` to `Users` and checks read/write lists case-insensitively.

## Dependencies and Integration
Integrates the library server with Win32 NT file store/security providers, settings helper types, network interface helper, and log writer.

## Risks and Test Signals
Risks include default integrated auth hiding settings users, plain-text passwords for independent auth, synchronous logging, no validation of share paths before server start, `Users` wildcard semantics tied to settings parsing, and no form-closing stop path. Test start/stop for both transports, bad settings file, access allow/deny matrix, name-server startup, checked-protocol invariants, and log writing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/ServerUI.cs -->
