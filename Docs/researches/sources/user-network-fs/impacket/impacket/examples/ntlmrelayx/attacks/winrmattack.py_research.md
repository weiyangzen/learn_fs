# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/winrmattack.py

## Purpose
`winrmattack.py` implements an interactive WinRM shell for relayed WinRMS sessions. It creates a remote WS-Man shell, sends commands through SOAP envelopes, receives base64 stdout streams, and cleans up the remote shell.

## Important APIs, Types, and Functions
- `PROTOCOL_ATTACK_CLASS = "WINRMAttack"` advertises the plugin.
- `WinRMShell(cmd.Cmd)` manages the local interactive command loop and remote WS-Man shell ID.
- `WinRMShell.onecmd()` sends command and receive SOAP messages.
- `WinRMShell.do_exit()` sends a WS-Man Delete request and closes the local TCP shell.
- `WINRMAttack(ProtocolAttack)` registers `PLUGIN_NAMES = ["WINRMS"]`, creates a `TcpShell`, and starts the shell in `run()`.

## Control Flow
`WINRMAttack.run()` listens on a local TCP shell, constructs `WinRMShell`, and enters `cmdloop()`. `WinRMShell.__init__` sends a Create request to `/wsman` and extracts `ShellId` with regex. Each command sends a Command request with the shell ID, extracts a `CommandId`, sends a Receive request, extracts stdout stream elements, base64-decodes them, and prints output. `do_exit()` deletes the remote shell and closes the TCP shell.

## State and Persistence Behavior
Local state includes TCP shell streams, prompt metadata, HTTP client, and the remote `shell_id`. Remote state is a WinRM shell and commands executed within it; `do_exit()` attempts cleanup. No local files are written.

## Dependencies and Integration Points
It depends on `cmd`, `sys`, `re`, `base64`, `impacket.LOG`, `ProtocolAttack`, and `TcpShell`. It assumes an HTTP client that can POST SOAP to `/wsman`.

## Risks and Edge Cases
- SOAP XML is assembled with f-strings and command text is not XML-escaped.
- Regex extraction of `ShellId`, `CommandId`, and streams is brittle and can throw when missing.
- Only stdout is decoded; stderr stream content is ignored.
- `onecmd("exit")` calls `do_exit()` but does not immediately return before building a command envelope.
- The plugin name is `WINRMS`, so plain `WINRM` targets may not map unless client code uses that name.

## Test Signals
Tests should fake HTTP responses for shell creation, command execution, receive output, missing IDs, base64 decode failures, exit cleanup, and command XML escaping expectations.
