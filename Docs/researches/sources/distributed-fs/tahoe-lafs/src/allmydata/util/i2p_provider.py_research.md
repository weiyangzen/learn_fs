# sources/distributed-fs/tahoe-lafs/src/allmydata/util/i2p_provider.py

## Purpose

This module implements Tahoe's I2P address-family provider. It detects optional dependencies, creates node-listener configuration for I2P destinations, validates `[i2p]` config, and supplies Foolscap client/listener endpoints that hide the node's public IP.

## APIs and control flow

`create()` builds `_Provider`, imports `foolscap.connections.i2p` and `txi2p`, and validates destination config. `is_available()` and `can_hide_ip()` report capability. `_try_to_connect()` probes a SAM endpoint with `txi2p.testAPI()`, trapping expected connection/auth failures. `_connect_to_i2p()` tries default or user-specified SAM ports. `create_config()` connects to I2P, generates a destination/private key, and returns `ListenerConfig` with `listen:i2p`, `i2p:<host>:<port>` location, and tahoe.cfg entries.

`_Provider.get_listener()` constructs an I2P server endpoint string from config. `get_client_endpoint()` chooses SAM, launch, configdir, or default client endpoint behavior. `check_dest_config()` enforces required keys and rejects unsupported launch combinations.

## State, dependencies, risks, and tests

Persistent state is the generated `private/i2p_dest.privkey` and tahoe.cfg `[i2p]` entries. Dependencies are Twisted endpoints/defer/service, txi2p, Foolscap I2P, Tahoe `ListenerConfig`, `_Config`, and `IAddressFamily`.

Risks include optional dependency absence, unsupported launch mode, endpoint-string escaping, fixed external port 3457, private-key file handling, and connection probes that may hang against non-SAM services. Test signals should cover unavailable dependencies, config validation errors, SAM endpoint probing, generated config entries, listener string escaping, disabled client endpoint, and all endpoint-selection branches.
