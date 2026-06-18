# sources/user-network-fs/impacket/tests/SMB_RPC/test_nmb.py

## Purpose

`test_nmb.py` validates Impacket NetBIOS name-service helpers locally with mocked packets and remotely against a configured Windows/Samba target. It covers NetBIOS name encode/decode behavior, node-status parsing, name lookups, host address resolution, and name registration request handling.

## Important APIs, Types, and Functions

The file defines `NMBLocalTests` and `NMBRemoteTests`. Local tests use `nmb.encode_name`, `nmb.decode_name`, `nmb.NetBIOS`, `nmb.NAME_SERVICE_PACKET`, `getnetbiosname`, `getnodestatus`, `gethostbyname`, and `name_query_request`. Remote tests inherit `RemoteTestCase`, call `set_transport_config()`, and use live `NetBIOS` calls against `self.machine` and `self.serverName`. `binascii.unhexlify` provides canned packet bytes, and `hexdump` is used for diagnostics.

## Control Flow

Local tests replace `NetBIOS.send` with a `send_hook` that returns `NAME_SERVICE_PACKET(mock)`, so each API consumes deterministic encoded packet bytes without sending UDP traffic. `test_encodedecodename` verifies that a long name is truncated to the NetBIOS 15-character payload. `test_getnetbiosname` parses a mocked node-status response into a server name. `test_getnodestatus` checks individual name table records. `test_gethostbyname` sets the name server and asserts the parsed IPv4 address. `test_name_query_request` directly exercises a name query response.

Remote tests repeat encode/decode and live network operations. They query the configured target's NetBIOS name, node status, host records, and registration behavior. The name registration test tolerates exceptions only when the message indicates a NetBIOS-level response; unrelated exceptions are re-raised.

## State and Persistence Behavior

Local tests keep all state in mock packet data and a `NetBIOS` instance whose `send` method and name server may be modified. Remote tests depend on `RemoteTestCase` state such as `machine`, `serverName`, and transport configuration. No files are written. Remote name registration may interact with the target's NetBIOS name service, but the test uses a throwaway name and catches expected NetBIOS errors.

## Dependencies and Integration Points

The module depends on `pytest.mark.remote`, Python `unittest`, the repository `tests.RemoteTestCase`, and `impacket.nmb`. It is an integration point between the packet structure parser, NetBIOS name encoding rules, and the higher-level query methods used by SMB discovery and connection setup.

## Risks and Edge Cases

The local tests depend on opaque hex captures, so packet-format intent is not obvious from the literals. Remote tests require a reachable target with NetBIOS services enabled, correct `RemoteTestCase` credentials/configuration, and network conditions that allow name service traffic. Encode/decode coverage explicitly checks long-name truncation, but the TODO notes that scope support is not fixed. Some remote tests print values without assertions, so they function more as smoke tests than strict correctness checks.

## Test Signals

Useful local signals are deterministic parsing of node-status and query responses and name truncation behavior. Useful remote signals are successful live lookups and tolerated NetBIOS registration errors. Changes to `impacket.nmb`, NetBIOS packet layouts, or SMB name resolution should run the local tests first and remote tests when a configured SMB/NetBIOS target is available.
