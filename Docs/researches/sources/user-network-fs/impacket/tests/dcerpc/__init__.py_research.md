# sources/user-network-fs/impacket/tests/dcerpc/__init__.py

Purpose: defines the base class for DCE/RPC endpoint integration tests. `DCERPCTests` turns remote configuration into a bound DCE/RPC connection using either a formatted string binding or endpoint-mapper resolution.

Important APIs and types: `DCERPCTests` inherits `RemoteTestCase` and defines constants `STRING_BINDING_FORMATTING`, `STRING_BINDING_MAPPER`, `TRANSFER_SYNTAX_NDR`, and `TRANSFER_SYNTAX_NDR64`. Configurable class attributes include `timeout`, `authn`, `authn_level`, `iface_uuid`, `protocol`, `string_binding`, `string_binding_formatting`, `transfer_syntax`, and `machine_account`. The main method is `connect()`.

Control flow: `setUp()` loads credentials, then formats `string_binding` with the test instance or uses `epm.hept_map()` for dynamic endpoint lookup. `connect()` creates a transport via `transport.DCERPCTransportFactory`, applies timeout and credentials when supported, obtains the DCE object, sets authentication level, connects, and binds to `iface_uuid` with optional transfer syntax.

State and persistence behavior: per-test mutable state is the resolved `string_binding` and credential attributes. No persistent files are written. Network handles are returned to callers, which are responsible for cleanup.

Dependencies and integration points: centralizes Impacket transport setup for all `tests/dcerpc/test_*.py` files. It depends on `impacket.dcerpc.v5.transport`, `epm`, and the shared remote config module.

Risks: `connect()` raises `NotImplemented` as an exception object rather than `NotImplementedError`. Tests relying on `string_binding` mutation in `setUp()` may be affected if the same instance reconnects with a changed class attribute. Authentication only applies when the transport has `set_credentials`; callers must handle transports without it. Returned DCE objects are not automatically disconnected.

Test signals: downstream remote tests passing across SMB named pipes, TCP endpoint mapper bindings, NDR, and NDR64 validates this base transport path.
