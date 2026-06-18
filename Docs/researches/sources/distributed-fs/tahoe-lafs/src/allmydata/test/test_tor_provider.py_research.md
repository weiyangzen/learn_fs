# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_tor_provider.py

## Purpose

This file tests `allmydata.util.tor_provider`, including Tor control-port connection attempts, launching Tor through txtorcon, generating Tor onion node configuration from CLI options, runtime provider handler/listener creation, onion configuration validation, and service start/stop behavior for hidden services.

The tests use mocks rather than real Tor or txtorcon processes. They focus on endpoint descriptions, configuration output, private-key file handling, Twisted Deferred behavior, and graceful absence of optional Tor dependencies.

## Important APIs, Types, and Helpers

`mock_txtorcon` and `mock_tor` patch provider import helpers so tests can simulate installed or missing optional dependencies. `make_cli_config` builds `CreateNodeOptions` with a parent `runner.Options`, basedir, stdout, and parsed CLI flags such as `--listen=tor`, `--tor-launch`, `--tor-executable`, and `--tor-control-port`.

`FakeTor` mimics a txtorcon Tor instance by exposing a `.protocol`. `FakeConfig` is a dict-backed Tahoe config facade with `get_config` and `get_config_path`. `EmptyContext` supports `tor.add_context` usage in handler-launch tests.

Main test classes map to provider internals: `TryToConnect` for `_try_to_connect`, `LaunchTor` for `_launch_tor`, `ConnectToTor` for `_connect_to_tor`, `CreateOnion` for `create_config`, `Provider` for `_Provider.get_tor_handler` and control endpoint memoization, `ProviderListener` for `get_listener`, `Provider_CheckOnionConfig` for validation, and `Provider_Service` for Twisted service lifecycle.

## Control Flow

`TryToConnect` patches `clientFromString`, calls `_try_to_connect`, and verifies successful `txtorcon.build_tor_connection`, handled `ConnectError` returning `None` with a stdout message, and unhandled errors propagating without stdout output.

`LaunchTor` patches `allocate_tcp_port`, calls `_launch_tor`, and checks that a Tor result is returned for default and explicit executable paths. `ConnectToTor` simulates trying default control endpoints (`unix:/var/run/tor/control`, `tcp:127.0.0.1:9051`, `tcp:127.0.0.1:9151`) or a CLI-specified endpoint, returning the first reachable protocol or raising `ValueError` if none are reachable.

`CreateOnion` verifies `create_config`. Missing txtorcon fails with a user-facing install message. Launch mode calls `_launch_tor`, allocates a local TCP port, creates an `EphemeralHiddenService`, adds/removes it from Tor, writes the private key to `private/tor_onion.privkey`, and emits `[tor]` config plus tub ports/locations. Control-endpoint mode uses `_connect_to_tor` instead and writes equivalent onion config with `control.port`.

`Provider` verifies `tor_provider.create` and `get_tor_handler`. Disabled config, missing `tor`, and launch-without-txtorcon return no handler. Launch mode creates a Tor control endpoint maker through `tor.control_endpoint_maker`, lazily launches Tor only once in `_make_control_endpoint`, then reuses the endpoint description. Socks and control endpoint configs call `clientFromString` and appropriate `tor.socks_endpoint` or `tor.control_endpoint`; default config uses `tor.default_socks`.

`ProviderListener` checks that `onion.local_port` becomes a `TCP4ServerEndpoint` on `127.0.0.1`. `Provider_CheckOnionConfig` validates combinations of `onion`, txtorcon availability, `launch`, `control.port`, `onion.local_port`, `onion.external_port`, and `onion.private_key_file`.

`Provider_Service` verifies service lifecycle. With `onion=False`, `startService` does not start an onion and toggles `running`. Launch mode reads a private key file, launches Tor, creates an `EphemeralHiddenService`, adds it to the Tor protocol, stores `_onion_ehs` and `_onion_tor_control_proto`, and removes the onion on `stopService`. Control-endpoint mode connects with `txtorcon.connect` through `clientFromString`, starts the hidden service, and removes it on stop.

## State and Persistence Behavior

`create_config` and service tests write private-key files beneath temporary basedirs, especially `private/tor_onion.privkey` for generated config and arbitrary `keyfile` paths for service startup. Runtime provider instances cache launch results for `_make_control_endpoint` so Tor is launched only once and endpoint descriptions are reused.

Provider service state includes Twisted `running`, `_onion_ehs`, and `_onion_tor_control_proto`. Onion hidden services are expected to be removed from Tor on stop. CLI config state is represented in `tor_config.node_config["tor"]`, `tor_config.tub_ports`, and `tor_config.tub_locations`.

## Dependencies and Integration Points

The tests integrate `allmydata.util.tor_provider` with Twisted endpoint parsing (`clientFromString`, `TCP4ServerEndpoint`), Twisted Deferreds, txtorcon APIs (`launch`, `connect`, `build_tor_connection`, `EphemeralHiddenService`, endpoint/handler factories), optional `tor` helper module APIs (`default_socks`, `socks_endpoint`, `control_endpoint`, `control_endpoint_maker`, `add_context`), Foolscap's eventual queue flushing, and Tahoe node-creation CLI parsing.

These are important startup/network integration points because Tor configuration affects tub ports, tub locations, onion key persistence, and client endpoint handlers.

## Risks and Edge Cases

The tests do not start real Tor, so they validate provider orchestration and API calls but not actual network behavior or txtorcon compatibility beyond mocked call shapes. Mocked objects sometimes use class objects rather than instances, so the tests emphasize identity/call arguments.

Configuration values in `FakeConfig` can be booleans, strings, or ints; production config parsing may normalize differently. Error-message assertions are exact and will fail on wording changes. Endpoint defaults and order are part of the contract in `_connect_to_tor`.

The launch-handler test relies on `flushEventualQueue` to allow lazy launch work to complete and verifies launch memoization. Changes to scheduling or context-manager behavior in tor integration may need updated synchronization.

## Test Signals

Passing tests signal that Tahoe can construct Tor client handlers and onion listeners from config, produce correct Tor-related node config during `create-node`, handle missing optional dependencies with clear errors or disabled behavior, cache lazy Tor launches, and cleanly add/remove onion services during service lifecycle.
