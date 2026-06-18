## sources/distributed-fs/tahoe-lafs/src/allmydata/listeners.py

### Purpose
This module defines a typed abstraction for listener providers used during Tahoe node creation. It lets transports such as TCP, Tor, and I2P report availability, privacy properties, generated tub configuration, and runtime address-family objects through a common protocol.

### Important APIs, Types, and Functions
`ListenerConfig` is an `attrs.frozen` value with `tub_ports`, `tub_locations`, and `node_config`. `Listener` is a `typing.Protocol` requiring `is_available`, `can_hide_ip`, async `create_config`, and `create`. `TCPProvider` implements plain TCP listener configuration, allocating a port with `allocate_tcp_port` when explicit `--port/--location` options are absent. `StaticProvider` is a frozen test/config helper that returns precomputed availability, privacy, config, and address-family behavior; its config may be an awaitable.

### Control Flow
Node creation selects one or more listener providers, asks whether each is available and whether it can hide IP addresses, awaits `create_config`, merges resulting `ListenerConfig` values into `tahoe.cfg`, then later calls `create` to obtain an `IAddressFamily`. `TCPProvider.create_config` either uses paired CLI port/location values or allocates a TCP port for the provided hostname.

### State and Persistence Behavior
`ListenerConfig` is the persistence boundary: its values are merged into the node configuration file. `TCPProvider` itself has no state. `StaticProvider` stores fixed constructor values and can defer config production until an awaitable resolves.

### Dependencies and Integration Points
The module depends on `attrs`, Twisted CLI `Options`, Tahoe `_Config`, `IAddressFamily`, and `allocate_tcp_port`. `scripts/create_node.py` imports these providers, while `util/tor_provider.py` and `util/i2p_provider.py` return compatible configs and address families.

### Risks and Edge Cases
TCP `create` is intentionally unimplemented, so using `TCPProvider` beyond config generation requires another path to instantiate address handling. Automatic port allocation can race with later bind attempts. CLI options must provide `--port` and `--location` together; the broader create-node code validates this. Merging multiple `node_config` values can conflict, as tested in create-node tests.

### Test Signals
`test/cli/test_create.py` covers `ListenerConfig` merge behavior and asynchronous `StaticProvider.create_config`. Tor/I2P provider tests and create-node integration tests exercise compatibility with this protocol.
