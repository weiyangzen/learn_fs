# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/smbattack.py

## Purpose
`smbattack.py` implements the default SMB relay attack. It can start an interactive SMB shell, install an executable as a service, run RPC sub-attacks over SMB named pipes, add machine accounts through SAMR, execute a command and retrieve output, enumerate local admins after access denial, or dump local SAM hashes.

## Important APIs, Types, and Functions
- `PROTOCOL_ATTACK_CLASS = "SMBAttack"` advertises the plugin.
- `SMBAttack(ProtocolAttack)` registers `PLUGIN_NAMES = ["SMB"]`.
- `__init__()` wraps raw SMB/SMB3 objects in `SMBConnection`, configures optional RPC attack transport, interactive `TcpShell`, or `ServiceInstall`.
- `__answer()` accumulates remote command output.
- `run()` dispatches RPC attack, interactive shell, service install, add-computer, command execution, or SAM dump.

## Control Flow
If `config.rpc_attack` is set, construction binds to `\atsvc` for TSCH or `\cert` for ICPR and creates an `RPCAttack`; `run()` delegates to it. Interactive mode starts `MiniImpacketShell`. Service mode installs and uninstalls the configured executable. Add-computer mode uses `RemoteOperations.connectSamr()` and SAMR calls to create a workstation trust account and set its password/control flags. Default admin mode enables remote registry, optionally executes a command and retrieves `ADMIN$\Temp\__output`, or saves SAM and dumps/export hashes.

## State and Persistence Behavior
Remote state can include named-pipe RPC calls, service creation/removal, SAMR machine-account creation, remote command execution, temporary output files, remote registry service state, and SAM hive reads. Local state includes the SMB connection wrapper, output buffer, optional TCP shell, service installer, and exported SAM hash files named from the remote host.

## Dependencies and Integration Points
It depends on Impacket SMB/SMB3/SMBConnection, DCERPC `tsch`, `icpr`, `samr`, `SMBTransport`, `RPCAttack`, `TcpShell`, `serviceinstall`, `MiniImpacketShell`, `RemoteOperations`, `SAMHashes`, and `EnumLocalAdmins`. It is a core ntlmrelayx attack plugin.

## Risks and Edge Cases
- Remote registry/service manipulation is intrusive and may leave artifacts on failure.
- Command execution relies on private `RemoteOperations` methods and a fixed temp output path.
- Add-computer password setting uses SAMR password change with a blank old NT hash and may fail depending on policies.
- SMB1 flag manipulation is performed to avoid invalid parameter errors.
- Local admin enumeration is only attempted on access denied and when configured.
- Many branches catch broad exceptions and log strings without structured recovery.

## Test Signals
Unit tests should fake SMB dialects, RPC attack setup, service install flow, SAMR add-computer calls, command output retrieval/deletion, registry access denial local-admin enumeration, and SAM dump cleanup. Integration tests need Windows SMB targets with controlled admin/non-admin relay accounts.
