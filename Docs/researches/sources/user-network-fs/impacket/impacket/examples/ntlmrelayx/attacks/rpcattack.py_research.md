# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/rpcattack.py

## Purpose
`rpcattack.py` implements RPC-based relay attacks for Task Scheduler command execution (`TSCH`) and AD CS ICPR certificate enrollment (`ICPR`). It also provides the `RPCAttack` dispatcher used directly for RPC targets and indirectly by SMB relay when binding named pipes.

## Important APIs, Types, and Functions
- `ELEVATED` tracks usernames already used for ICPR certificate requests.
- `TSCHRPCAttack._xml_escape()` and `_run()` build/register/run/delete a scheduled task executing `config.command`.
- `ICPRRPCAttack._run()` builds a CSR and calls `icpr.hCertServerRequest()`, then writes a PFX.
- `RPCAttack(ProtocolAttack, TSCHRPCAttack)` registers `PLUGIN_NAMES = ["RPC"]`, stores DCE transport/stringbinding/endpoint, and dispatches by `config.rpc_mode`.

## Control Flow
For TSCH, `_run()` creates a random task name, builds a UTF-16 task XML running `cmd.exe /C <command>` as LocalSystem, registers it over DCERPC, runs it, polls `SchRpcGetLastRunInfo` until a nonzero runtime appears, deletes the task, and logs completion. For ICPR, `_run()` generates a key/CSR, chooses a template, requests a certificate over the ICPR RPC interface, handles common DCERPC errors, converts DER to a certificate, serializes a PFX, and writes it to `lootdir`.

## State and Persistence Behavior
TSCH mutates remote scheduled-task state temporarily and executes a command without output collection. ICPR creates CA request/certificate state and writes a local `.pfx`. `ELEVATED` is process-global and username-keyed.

## Dependencies and Integration Points
It depends on `OpenSSL.crypto`, `cryptography.x509`, Impacket DCERPC modules `tsch` and `icpr`, `NULL`, `DCERPCSessionError`, `ADCSAttack` helpers, and `ProtocolAttack`. `SMBAttack` can instantiate `RPCAttack` after binding to `\atsvc` or `\cert`.

## Risks and Edge Cases
- TSCH command output is not captured; success is inferred from last run info.
- Polling can wait indefinitely if last run info never updates.
- XML escaping covers core characters but command semantics remain operator-controlled.
- ICPR PFX is unencrypted, and the global `ELEVATED` cache is not target-specific.
- Certificate request behavior depends on template, CA name, and RPC encryption requirements.

## Test Signals
Unit tests should fake DCE calls for task XML creation, run polling, delete behavior, ICPR success/failure codes, PFX filename generation, and duplicate-user skipping. Integration tests require TSCH and ICPR-accessible Windows targets.
