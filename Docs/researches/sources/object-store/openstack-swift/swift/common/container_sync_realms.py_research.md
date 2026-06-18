# sources/object-store/openstack-swift/swift/common/container_sync_realms.py

## Purpose
`container_sync_realms.py` loads `container-sync-realms.conf` and exposes realm keys, secondary keys, cluster endpoints, cluster lists, and request signatures for Swift container sync. It periodically reloads the config based on file modification time to allow key and endpoint changes without process restart.

## Important APIs, types, and functions
- `ContainerSyncRealms.__init__(conf_path, logger)` initializes reload timers, mtime tracking, data storage, and forces an initial reload.
- `reload()` resets mtime state and delegates to `_reload()`.
- `_reload()` checks mtime no more often than `mtime_check_interval`, parses the config, updates reload interval, and rebuilds uppercase realm/cluster mappings.
- `realms()`, `key()`, `key2()`, `clusters()`, and `endpoint()` are lookup methods that refresh if needed before returning data.
- `get_sig(request_method, path, x_timestamp, nonce, realm_key, user_key)` creates the HMAC-SHA1 hex signature over method, path, timestamp, nonce, and user key using the realm key.

## Control flow
Lookup methods call `_reload()`, which only stats the file when the next mtime-check deadline has passed. Missing files are logged at debug level; other stat errors and parse errors are logged as errors. When mtime changes, the config is read, `DEFAULT/mtime_check_interval` is optionally parsed, and each section becomes an uppercase realm. Options named `key` or `key2` become realm secrets; options beginning `cluster_` become uppercase cluster names mapped to endpoint URLs.

Signature generation coerces nonce and keys to valid UTF-8 strings, encodes path if it is a Python string, then computes an HMAC using a newline-joined byte payload and SHA1.

## State and persistence behavior
State is in-memory: config path, next check time, mtime interval, last mtime, and parsed realm data. The file reads configuration from disk but does not write. Key rotation is supported by reloading both primary and secondary keys when the config mtime changes.

## Dependencies and integration points
It depends on `configparser`, filesystem mtime, logging, `hmac`/`hashlib`, and `get_valid_utf8_str`. Container sync middleware and daemons use it to discover allowed remote realms/clusters and to validate or generate sync signatures.

## Risks and edge cases
If config parsing fails after a previous successful load, old data remains in memory because `self.data` is only replaced after successful parsing. That is resilient but can delay key revocation. The reload interval is itself read from the file, so an invalid interval logs an error and leaves current data behavior dependent on the surrounding parse branch. Cluster and realm names are case-normalized to uppercase, while endpoint values are not normalized. SHA1 HMAC remains the protocol contract; changing it would break compatibility.

## Test signals
Tests should cover missing file logging, mtime-based reload suppression, forced reload, parse errors preserving prior data, interval parsing, uppercase realm/cluster lookup, key/key2 lookup, endpoint lookup, signature byte construction for str and bytes paths, and UTF-8 coercion of nonce and keys.
