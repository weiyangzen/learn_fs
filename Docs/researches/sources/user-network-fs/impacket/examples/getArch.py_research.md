# sources/user-network-fs/impacket/examples/getArch.py

## Purpose

`getArch.py` remotely infers whether Windows targets are 32-bit or 64-bit by attempting to bind to the endpoint mapper with the NDR64 transfer syntax over TCP port 135. It requires no authentication and supports either a single target or a file of targets.

## Important APIs, Types, and Functions

`TARGETARCH` stores CLI options, a machine list, and the NDR64 syntax tuple `('71710533-BEBA-4937-8319-B5DBEF9CCC36', '1.0')`. `TARGETARCH.run()` reads targets, creates `DCERPCTransportFactory` bindings, sets connect timeouts, connects, and calls `dce.bind(MSRPC_UUID_PORTMAP, transfer_syntax=self.NDR64Syntax)`.

## Control Flow

The command validates that `-target` or `-targets` is present, initializes logging, and runs `TARGETARCH`. For each machine, it connects to `ncacn_ip_tcp:<machine>[135]`. If the NDR64 bind fails with `syntaxes_not_supported`, the target is printed as 32-bit. If the bind succeeds, it is printed as 64-bit. Other DCE/RPC or socket errors are logged per target and processing continues.

## State and Persistence Behavior

State is limited to the in-memory target list and transient DCE/RPC connections. No authentication state, local files, or remote changes are produced. The `-targets` file is read line by line and stripped.

## Dependencies and Integration Points

The script uses Impacket DCE/RPC transport, endpoint mapper UUID constants, and `DCERPCException`. It integrates with Windows RPC endpoint mapper behavior documented by Microsoft. It is intentionally not reliable for Samba and has unknown macOS behavior.

## Risks and Edge Cases

The architecture inference depends on endpoint mapper transfer-syntax behavior, not an explicit OS architecture API. Firewalls, non-Windows RPC stacks, Samba, port filtering, or endpoint mapper hardening can lead to errors or misleading output. Input files are not de-duplicated and blank lines become connection attempts. Only the substring `syntaxes_not_supported` is treated as a 32-bit signal.

## Test Signals

Unit tests can mock DCE bind outcomes for success, `syntaxes_not_supported`, and unrelated failures. Integration tests need known 32-bit and 64-bit Windows systems or captured DCE/RPC behavior. CLI tests should cover target file parsing, timeout propagation, missing-target validation, and continued processing after one target fails.
