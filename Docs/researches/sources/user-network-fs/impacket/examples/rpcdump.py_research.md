# sources/user-network-fs/impacket/examples/rpcdump.py

## Purpose

`rpcdump.py` queries a remote DCE/RPC endpoint mapper and prints registered interfaces grouped by UUID, provider, protocol, annotation, and string bindings. It supports common endpoint mapper transports over TCP, SMB named pipes, RPC over HTTP, and RPC proxy.

## Important APIs, Types, and Functions

`RPCDump.KNOWN_PROTOCOLS` maps ports 135, 139, 443, 445, and 593 to binding string templates. `RPCDump.__init__()` stores credentials, hashes, and selected port. `dump()` builds the transport, applies SMB or HTTP proxy authentication as needed, calls `__fetchList()`, groups endpoint entries, maps UUIDs through `epm.KNOWN_UUIDS` and `epm.KNOWN_PROTOCOLS`, and prints the results. `__fetchList()` connects and calls `epm.hept_lookup()`.

## Control Flow

The CLI parses target, target IP, endpoint mapper port, hashes, logging flags, and optional password prompt. `dump()` chooses the binding string from the port, configures credentials for SMB transports or RPC proxy, then fetches endpoint entries. Exceptions are logged, with special explanations for common RPC proxy failures. Successful results are grouped by interface UUID and printed with all bindings.

## State and Persistence Behavior

The script is read-only against the target endpoint mapper. It opens network connections and prints discovered metadata; it writes no local files and creates no remote state.

## Dependencies and Integration Points

It uses Impacket `transport`, `epm`, `uuid`, RPC over HTTP error constants, `AUTH_NTLM`, and `parse_target`. It integrates with Windows/Samba endpoint mappers and RPC proxy deployments.

## Risks and Edge Cases

The port must be one of the hard-coded choices. RPC proxy support assumes NTLM for proxy authentication. Endpoint annotations are decoded as UTF-8 after stripping the trailing null and can fail for unexpected encodings. `__fetchList()` does not use `finally` for disconnect, so exceptions before disconnect can leave sockets until process exit.

## Test Signals

Tests can mock `epm.hept_lookup()` responses and verify grouping, provider/protocol lookup, binding formatting, and port-specific credential setup. Integration coverage should query ports 135, 445, 593, and a negative RPC proxy scenario.
