# sources/user-network-fs/impacket/tests/misc/test_socksserver.py

Purpose: Regression-tests SOCKS request handling for a successful relay tunnel to ensure no extra failure reply is sent.

Important APIs, types, and functions: Uses `SocksRequestHandler`, `socket`, `struct`, `unittest.mock`, and `_SuccessfulRelay` with `initConnection`, `skipAuthentication`, and `tunnelConnection`.

Control flow: Builds a mock SOCKS5 connection with greeting and connect request bytes, injects server relay/plugin state into a manually allocated handler, runs `handle`, and asserts two sends plus relay `inUse` cleanup.

State and persistence behavior: Uses mock socket/server state only. The handler mutates `activeRelays` in memory by toggling `inUse`.

Dependencies and integration points: Covers ntlmrelayx SOCKS server integration with protocol plugin lifecycle.

Risks: Manual private-attribute setup is brittle if handler internals are renamed. The test is narrow but targets a user-visible protocol bug.

Test signals: Confirms successful tunnel path sends only expected SOCKS replies and releases relay state after handling.
