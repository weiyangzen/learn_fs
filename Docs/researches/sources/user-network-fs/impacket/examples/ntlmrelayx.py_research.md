# sources/user-network-fs/impacket/examples/ntlmrelayx.py

## Purpose

`ntlmrelayx.py` is the top-level orchestration script for Impacket’s NTLM relay framework. It starts one or more inbound relay servers, configures protocol clients and attack modules, processes target selection, optionally exposes a SOCKS proxy and mini-shell, and keeps the process alive while relayed authentications are handled by the imported framework components.

## Important APIs, Types, and Functions

`RELAY_SERVERS` is populated with selected server classes such as `SMBRelayServer`, `HTTPRelayServer`, `WCFRelayServer`, `RAWRelayServer`, `RPCRelayServer`, `WinRMRelayServer`, `WinRMSRelayServer`, `MSSQLRelayServer`, and `RDPRelayServer`. `start_servers()` creates an `NTLMRelayxConfig` for each server, injects `PROTOCOL_CLIENTS`, `PROTOCOL_ATTACKS`, target processors, attack flags, protocol-specific settings, listening ports, WPAD/WebDAV/exploit options, AD CS, shadow credentials, and SCCM options, then starts server threads.

`stop_servers()` shuts down running relay server objects. `MiniShell` exposes runtime commands for target listing, finished attacks, SOCKS relay table display via the local HTTP API, and start/stop of relay listeners.

## Control Flow

The main block builds a large argparse surface grouped by server, SMB, RPC, MSSQL, HTTP, LDAP, IMAP, AD CS, shadow credentials, and SCCM options. After validation, it imports protocol client and attack registries, chooses relay mode from `-t` or `-tf` or reflection mode when no target exists, fills `RELAY_SERVERS` according to disabled server flags, optionally starts a target-file watcher, optionally starts a SOCKS server thread, chooses an interface bind address, and calls `start_servers()`. It then waits on `MiniShell.cmdloop()` when SOCKS mode is enabled or `stdin.read()` otherwise.

## State and Persistence Behavior

Runtime state lives in server threads, target processors, target-file watcher threads, the optional SOCKS server, and the global `RELAY_SERVERS` list. Persistence depends on configured attacks and options: loot and dumps are written under `-lootdir`, encrypted hashes may be written using `-output-file`, certificates or keys may be exported by shadow-credential attacks, and SCCM/LDAP/SMB attacks can modify remote services, LDAP attributes, DNS records, or domain objects through imported attack modules.

## Dependencies and Integration Points

The script is a central integration point for `impacket.examples.ntlmrelayx.servers`, `utils.config.NTLMRelayxConfig`, `utils.targetsutils.TargetsProcessor` and `TargetsFileWatcher`, `servers.socksserver.SOCKS`, protocol clients, and attack registries. It binds network services on privileged ports by default and depends on target-specific protocol support and security settings such as SMB signing, EPA, channel binding, SPN checks, and NTLM policies.

## Risks and Edge Cases

The option surface permits high-impact remote changes, including ACL abuse, DNS record creation, SCCM registration, AD CS enrollment, shadow credentials, and command execution. The SCCM validation assumes `options.target` is present when SCCM flags are set; using SCCM flags without a target can raise before a clean argparse error. `MiniShell.printTable()` assumes at least one row before computing max widths, though callers check item length. `stop_servers()` only shuts down instances of configured relay server classes, not auxiliary watcher or SOCKS threads. Privileged bind failures and partial server startup are mostly delegated to server implementations.

## Test Signals

Test signals include parser validation for incompatible RPC and SCCM options, `parse_listening_ports()` handling of ranges, correct `RELAY_SERVERS` population from disable flags, config setters called with expected values for HTTP, SMB, LDAP, AD CS, SCCM, and SOCKS options, MiniShell filter output, target-file watcher activation, and clean startup/shutdown of selected server classes under mocked network sockets.
