# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/create_node.py

## Purpose
Implements `tahoe create-node`, `create-client`, and `create-introducer`. It validates listener/privacy options, creates node directories, writes compatibility `.tac` files, generates `tahoe.cfg`, optionally joins an invited grid via magic-wormhole, and writes introducer configuration.

## APIs, Types, And Control Flow
Option classes are `CreateClientOptions`, `CreateNodeOptions`, and `CreateIntroducerOptions`. `validate_where_options`, `validate_tor_options`, and `validate_i2p_options` enforce combinations of `--listen`, `--hostname`, `--port`, `--location`, Tor, I2P, and hidden-IP settings. `write_node_config` asynchronously asks listener providers for `ListenerConfig`, merges configs, writes `[connections]`, `[node]`, tub port/location, and listener sections. `write_client_config` writes client, storage, and helper sections. `create_node` refuses non-empty basedirs, handles wormhole invite overrides through a whitelist, creates `private`, writes config, and prints setup reminders. `create_client` forces no storage and no listening; `create_introducer` writes only node config.

## State, Persistence, And Integration
Creates the basedir, `private/`, `tahoe-client.tac` or `tahoe-introducer.tac`, `tahoe.cfg`, and possibly `private/introducers.yaml`. It integrates with listener providers (`tcp`, `tor`, `i2p`, `none`), Twisted Deferred/coroutine bridging, magic-wormhole, encoding/file utilities, and CLI runner dispatch.

## Risks And Test Signals
Risks include option-combination gaps, listener config overlap errors, partial directory creation if async listener setup fails, sensitive invite data handling, and hidden-IP misconfiguration if listener capabilities change. `--i2p-launch` is explicitly not implemented. Test signals are `allmydata/test/cli/test_create.py`, listener/Tor/I2P provider tests, and invite tests.
