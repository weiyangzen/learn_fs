# sources/user-network-fs/impacket/tests/SMB_RPC/test_rpch.py

## Purpose

`test_rpch.py` validates RPC over HTTP support. It combines one remote smoke test against `ncacn_http` endpoint mapper with local golden tests for RTS packet parsing and command serialization.

## Important APIs, Types, and Functions

`RPCHTest(RemoteTestCase, unittest.TestCase)` uses `transport.DCERPCTransportFactory`, a `dce` object, `epm.MSRPC_UUID_PORTMAP`, `epm.ept_lookup`, and endpoint mapper constants. `RPCHLocalTest` uses `rpch.RTSHeader`, `rpch.COMMANDS`, and specific RTS command structures such as `Version`, `ReceiveWindowSize`, `Cookie`, `ConnectionTimeout`, `Ack`, `RTSCookie`, and `ChannelLifetime`. `struct.unpack('<L', ...)` decodes command IDs from raw PDU data.

## Control Flow

The remote test builds `ncacn_http:<machine>`, connects without authentication, binds to endpoint mapper, sends an `ept_lookup` request, disconnects, reconnects, and repeats the same request. This primarily checks connection setup and reconnect behavior for RPC over HTTP v1.

Local tests parse captured RTS PDUs. Each test constructs a byte string for a specific scenario, instantiates `RTSHeader`, reads `pduData` and `NumberOfCommands`, then loops over commands by reading the command type and instantiating the matching class from `rpch.COMMANDS`. Assertions check flags, fragment length, pdu data length, and command `getData()` round trips. Scenarios include CONN/A1, CONN/A3, PING, CONN/C2, FlowControlAckWithDestination, CONN/B2 IPv4, and CONN/A2.

## State and Persistence Behavior

The local tests are stateless beyond parsed packet objects and command lists. The remote test depends on `RemoteTestCase` configuration and opens real RPC-over-HTTP connections, but it does not write files or modify persistent target state. The reconnect sequence intentionally creates two connection lifecycles in one test.

## Dependencies and Integration Points

The module depends on `pytest.mark.remote`, `RemoteTestCase`, `impacket.dcerpc.v5.transport`, `epm`, and `rpch`. It integrates the RTS parser with DCE/RPC transport creation and endpoint mapper requests, exercising both low-level command structures and high-level transport behavior.

## Risks and Edge Cases

The local parsing loop trusts the command type lookup and command length calculations; an incorrect command length can desynchronize later commands. Captured RTS packets include channel flags, cookies, receive windows, timeouts, flow-control acknowledgements, and partially noted IPv4 address padding behavior. The remote test requires an RPC over HTTP endpoint to be exposed and may fail in environments where the service is disabled or firewalled.

## Test Signals

Local signals are exact `getData()` matches for selected RTS commands and expected header flags/lengths. Remote signal is successful unauthenticated connect/bind/request/disconnect/reconnect over `ncacn_http`. This file should be run after modifications to `rpch.py`, RTS command definitions, DCE/RPC HTTP transport state, and endpoint mapper transport selection.
