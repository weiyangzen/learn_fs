# sources/user-network-fs/impacket/examples/exchanger.py

## Purpose
`exchanger.py` targets Microsoft Exchange RPC over HTTP v2, currently through the NSPI address book interface. It lists address book tables, dumps table rows, resolves known object GUIDs, and brute-lookups Distinguished Name Tags (DNTs) to retrieve directory properties exposed through Exchange.

## Important APIs, Types, and Functions
`Exchanger` is a base class for credentials, output options, binary encoding, optional output file handling, and abstract connection hooks. `NSPIAttacks` implements RPC/NSPI operations. It defines minimal, extended, and GUID-only property sets, connects over `ncacn_http:%s[6004,RpcProxy=%s:443]`, binds to `nspi.MSRPC_UUID_NSPI`, and stores an NSPI context handle.

Key methods include `load_htable()`, `_parse_and_set_htable()`, `load_htable_stat()`, `print_htable()`, `load_props()`, `req_print_table_rows()`, `req_print_guid()`, `_req_print_guid()`, and `req_print_dnt()`. `ExchangerHelper` validates submodule options, constructs `NSPIAttacks`, and dispatches `list-tables`, `dump-tables`, `guid-known`, and `dnt-lookup`. The CLI uses `parse_target()`, optional Basic auth, hashes, `-rpc-hostname`, row batching, output type, output file, and Python-version-aware required subparsers.

## Control Flow
Main parses credentials and module/submodule options, prompts for a password, normalizes `-rpc-hostname`, and calls `ExchangerHelper.run()`. NSPI runs validate arguments before connecting. `connect_rpc()` builds the string binding, sets credentials and optional Basic auth, sets DCE auth level 6, connects, binds, and performs `hNspiBind()`.

`list-tables` loads the special hierarchy table and optionally per-table counts. `dump-tables` chooses a property set, resolves a named or GUID table to a Minimal Entry ID, and pages through rows with `hNspiQueryRows()`. Full and extended lookups first request `PR_INSTANCE_KEY` values to avoid resource errors, then query explicit tables. `guid-known` converts GUIDs to legacy DNs and resolves them with `hNspiResolveNamesW()`. `dnt-lookup` walks DNT ranges in batches and first checks whether rows are nonempty before printing extended/full/GUID output.

## State and Persistence
The tool keeps an NSPI context handle, current `STAT`, hierarchy table metadata, property lists, output options, and an optional output file descriptor. It does not mutate Exchange or AD state. It can persist dumped directory data to a user-specified output file while also printing to stdout.

## Dependencies and Integration Points
The script integrates with Impacket RPC over HTTP transport, NSPI structures, MAPI property metadata, Exchange RPC Proxy error constants, and NTLM/Basic HTTP authentication. It depends on Exchange exposing the RPC Proxy/NSPI endpoint and, for autodetection fallback, can require a manually supplied RPC server name.

## Risks
The tool can enumerate sensitive address book and directory attributes. The `dnt-lookup` path includes explicit warnings that malformed or unsupported DNT ranges can crash `ntdsai.dll` in `lsass.exe` and reboot a domain controller in some multi-tenant environments. Basic auth without a domain can fail or expose credentials to unsuitable endpoints. Large FULL dumps can be resource-intensive. The base method is misspelled `conenct_mapi`, although unused here.

## Test Signals
Unit-style tests can cover property row printing, binary hex/base64 encoding, hierarchy parsing, DNT range stepping, option validation, and output-file writing. Integration tests need Exchange RPC over HTTP with NSPI, valid and invalid RPC hostnames, NTLM and Basic authentication, GAL and custom address books, GUID lookup files with comments/blanks, and controlled DNT ranges to validate safety checks and error messages.
