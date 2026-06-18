# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_node.py

## Purpose
Tests Tahoe node configuration parsing, Tub location/listener setup, private config handling, privacy constraints, disabled-listener validation, invalid config rejection, and default connection handlers.

## APIs / Types / Functions
- `testing_tub` builds a main Tub from config text using I2P/Tor providers and connection handlers.
- `TestCase` covers FURL locations, config parsing, private config, config writes, timestamp formatting, secret directory permissions, log-dir type, and `_Config.set_config`.
- `TestMissingPorts` covers `_tub_portlocation` edge cases.
- `FakeTub`/`Listeners` test `tub_listen_on`.
- `ClientNotListening`, `IntroducerNotListening`, `Configuration`, and `CreateDefaultConnectionHandlersTests` cover higher-level startup validation.

## Control Flow
Location tests create node dirs, configure tub port/location, optionally patch local addresses, register references, and inspect FURL hints. Config tests write/read `tahoe.cfg` and private files, checking missing entries, unreadable files, persistence, invalid config, and unescaped FURL hashes. Port/location tests cover `AUTO`, defaults, disabled pairs, empty values, mismatched disabled values, and privacy rejection for TCP hints. Listener tests validate multiple TCP endpoints and Tor/I2P provider listener delegation. Disabled-listener tests reject storage/helper/introducer modes without listening Tubs.

## State And Persistence
Creates many basedirs, `tahoe.cfg`, private config files, secrets directories, permission changes, fake/real Tubs, and endpoint assigner state.

## Dependencies / Integration Points
Central integration with `allmydata.node`, `allmydata.client`, introducer creation, I2P/Tor providers, Foolscap Tub setup, config validation, filesystem permissions, Hypothesis port generation, and Twisted platform behavior.

## Risks And Test Signals
Permission tests skip on Windows or superuser. Some tests validate formatting without real binding. Passing tests show safe config parsing/persistence, private config handling, no-IP-leak enforcement, listener delegation, and rejection of invalid or impossible node modes.
