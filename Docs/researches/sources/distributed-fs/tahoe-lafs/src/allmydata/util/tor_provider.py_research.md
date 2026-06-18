# sources/distributed-fs/tahoe-lafs/src/allmydata/util/tor_provider.py

## Purpose

This module implements Tahoe's Tor address-family provider. It detects optional Tor dependencies, creates onion-service listener configuration, launches or connects to Tor control ports, creates Foolscap Tor client endpoints, and starts/stops configured onion services.

## APIs and control flow

`is_available()` checks Foolscap Tor and txtorcon. `create()` injects optional import hooks and validates onion config. `_try_to_connect()`, `_connect_to_tor()`, and `_launch_tor()` probe or launch Tor control connections. `create_config()` either launches Tor or connects to an existing control port, creates an ephemeral hidden service, captures hostname/private key, removes the temporary service, writes `private/tor_onion.privkey`, and returns `ListenerConfig` with localhost server endpoint, Tor location, and `[tor]` config entries.

`_Provider.get_listener()` binds local onion backend TCP. `get_client_endpoint()` chooses launched-control, SOCKS, explicit control, or default SOCKS behavior. `_get_launched_tor()` memoizes launch with `OneShotObserverList`. `_start_onion()` reads the stored private key and adds the hidden service. `stopService()` removes it.

## State, dependencies, risks, and tests

Persistent state is the onion private key and tahoe.cfg `[tor]` entries. Runtime state includes launched Tor, active hidden service, and control protocol references. Dependencies are Twisted endpoints/service/defer, txtorcon, Foolscap Tor, local observer and port allocation, and `ListenerConfig`.

Risks include optional dependencies, fixed external port 3457, private-key file permissions, launched Tor lifecycle not fully stopped, control-port auth failures, endpoint selection conflicts, and onion removal on shutdown failures. Test signals should cover dependency absence, launch/connect branches, generated config and key file, provider validation, client endpoint selection, memoized launch, start/stop onion service, and connection failure trapping.
