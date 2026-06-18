# sources/object-store/openstack-swift/swift/common/middleware/crypto/kmip_keymaster.py

## Purpose
`kmip_keymaster.py` adapts `BaseKeyMaster` to fetch root encryption secrets from a KMIP service via PyKMIP. It lets operators reference one or more KMIP key ids instead of storing root secrets directly in Swift config.

## Important APIs, Types, and Functions
`KmipKeyMaster` defines `log_route`, supported config options, config section name, `_load_keymaster_config_file()`, and `_get_root_secret()`. `filter_factory()` returns the keymaster filter.

## Control Flow
Config loading delegates to `BaseKeyMaster`, then determines the actual config section, rejects directory-style proxy config, attaches Swift logger handlers to the `kmip` logger, and installs filters that prevent sensitive DEBUG logging from PyKMIP protocol/config loggers. It creates `ProxyKmipClient` from the chosen config. `_get_root_secret()` iterates `key_id*` multikey options, fetches each KMIP object, verifies it is AES-256, caches duplicate KMIP ids to avoid extra round trips, and returns secret bytes keyed by Swift secret id.

## State and Persistence
Root secrets fetched from KMIP are stored in memory by the base class. KMIP keys remain external persistent state. The module itself writes no Swift metadata beyond what base keymaster/encryption later persist.

## Dependencies and Integration Points
It depends on `kmip.pie.client.ProxyKmipClient`, Python logging, Swift `LogLevelFilter`, multikey option parsing, and all `BaseKeyMaster` behavior. It replaces the default keymaster in the proxy pipeline.

## Risks and Edge Cases
Startup depends on KMIP availability and valid client TLS/auth config. Incorrect KMIP algorithm or key length is rejected. Sensitive logging filters are important because PyKMIP debug logs may include key material or passwords. Directory config is unsupported without `keymaster_config_path`.

## Test Signals
Tests should cover external config loading, directory-config rejection, logger/filter setup, multikey and duplicate KMIP id handling, AES-256 validation, invalid algorithm/length errors, active secret selection inherited from base, and client context-manager failures.
