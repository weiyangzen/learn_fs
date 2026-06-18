# sources/object-store/openstack-swift/swift/common/middleware/crypto/keymaster.py

## Purpose
`keymaster.py` provides the default Swift encryption keymaster. It loads one or more high-entropy root secrets and installs a request-local callback that derives account/container/object encryption keys from request paths using HMAC-SHA256.

## Important APIs, Types, and Functions
`KeyMasterContext.fetch_crypto_keys()` is the callback installed under `swift.callback.fetch_crypto_keys`. `BaseKeyMaster` provides config-file loading, root-secret validation, request routing, and `create_key()`. `KeyMaster` loads base64 `encryption_root_secret*` options and decodes them. `filter_factory()` exposes the filter.

## Control Flow
`BaseKeyMaster.__init__()` optionally loads a separate keymaster config, calls subclass `_get_root_secret()`, normalizes single secret to a dict, validates `active_root_secret_id`, and validates metadata-version configuration. For PUT/POST/GET/HEAD Swift requests, `__call__()` creates a `KeyMasterContext`, which preserves any alternate upstream key callback, installs its own callback, then calls downstream. `fetch_crypto_keys()` derives keys for requested or stored key ids, handles metadata versions 1, 2, and 3, includes key ids and `all_ids` for rotation, and falls back to alternate callbacks for unknown secret ids when present.

## State and Persistence
Root secrets are held in process memory. Persistent crypto metadata contains opaque key ids with version, path, and optional secret id. No derived keys are persisted. `KeyMasterContext` caches derived key dicts per request.

## Dependencies and Integration Points
It depends on Swift config reading, strict base64 decoding, multikey option loading, path splitting, `WSGIContext`, and `UnknownSecretIdError`. It must appear before the encryption middleware so crypto code can fetch keys.

## Risks and Edge Cases
Changing or losing root secrets makes encrypted data unreadable. Metadata-version compatibility handles historic path bugs, including object names starting with slash and old py3 WSGI-string metadata. `keymaster_config_path` forbids overlapping keymaster options in the filter section to avoid ambiguous config. Unknown active secret ids and short/non-bytes secrets fail at startup.

## Test Signals
Tests should cover root secret decoding and minimum length, multikey loading, active secret selection, config-file conflict detection, metadata versions, path derivation for account/container/object, historic path bug compatibility, all_ids rotation behavior, alternate callback fallback, request-method routing, and unknown secret errors.
