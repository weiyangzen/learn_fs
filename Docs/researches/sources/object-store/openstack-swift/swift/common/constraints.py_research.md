# sources/object-store/openstack-swift/swift/common/constraints.py

## Purpose
`constraints.py` defines Swift request and metadata limits, loads deployer overrides from `swift.conf`, and provides validation helpers for object creation, metadata headers, drive/mount paths, delete scheduling headers, UTF-8 safety, account/container name formatting, timestamps, and API versions.

## Important APIs, types, and functions
- Module constants define default max file size, metadata name/value/count/overall limits, header and request-line limits, object/account/container name limits, listing limits, valid API versions, extra header allowance, and auto-create account prefix.
- `DEFAULT_CONSTRAINTS`, `OVERRIDE_CONSTRAINTS`, and `EFFECTIVE_CONSTRAINTS` track default, configured, and active values.
- `reload_constraints()` reads `utils.SWIFT_CONF_FILE` section `swift-constraints`, converts values based on default types, updates globals, and populates effective constraints.
- `MAX_HEADER_COUNT` is derived from metadata count, Swift internal/default headers, and extra header count.
- `check_metadata(req, target_type)` validates metadata header names, values, count, aggregate size, header value length, and UTF-8 constraints for account/container metadata.
- `check_object_creation(req, object_name)` validates message length, content length or chunked transfer, object name length, content type, delete headers, content-type UTF-8, and object metadata.
- `check_dir()`, `check_mount()`, and `check_drive()` validate device names and mount/directory existence.
- `valid_timestamp()`, `check_delete_headers()`, `check_utf8()`, `check_name_format()`, and `valid_api_version()` are shared request validation helpers.

## Control flow
At import time `reload_constraints()` applies config overrides and updates module-level uppercase names. Metadata validation iterates every header, first rejecting overlong string header values, then checking only the `x-<target>-meta-` prefix for metadata-specific limits. Object creation reads `req.message_length()`, maps malformed length/transfer-encoding problems to HTTP exceptions, enforces object size and content-type requirements, normalizes delete scheduling headers, and delegates metadata validation.

Drive validation rejects names whose URL-quoted form differs, then requires either `utils.ismount(path)` or `isdir(path)` depending on mount-check mode. Delete-header validation converts `X-Delete-After` to `X-Delete-At`, normalizes timestamps, and rejects past deletion times except backend replication requests. UTF-8 validation accepts strings or bytes that round-trip as UTF-8, rejects surrogate code points, rejects null bytes unless Swift's reserved-byte setting differs, and rejects Swift's reserved byte unless `internal=True`.

## State and persistence behavior
The module has process-global mutable constraint state. Reloading constraints changes module constants that other modules may have imported by value or may read dynamically. Request validation mutates the request headers when `X-Delete-After` is converted to `X-Delete-At`. No persistent storage is written.

## Dependencies and integration points
It integrates with `swift.common.utils` for config path, CSV parsing, mount detection, timestamp normalization, reserved byte, and boolean parsing; with Swift exceptions for invalid timestamps; and with `swob` HTTP exceptions and WSGI string/byte conversion. Proxy, account, container, object, and backend code rely on these helpers before accepting user and internal requests. `bufferedhttp.py` uses `MAX_HEADER_COUNT` to adjust parser limits.

## Risks and edge cases
Import-time config loading means tests and services must call `reload_constraints()` after changing `SWIFT_CONF_FILE`. `MAX_HEADER_COUNT` is computed after import and may not update if constraints are reloaded with a different metadata count or extra header count unless code recomputes it separately. Metadata UTF-8 rules differ by target type: object metadata can contain values that account/container metadata would reject. `check_object_creation()` mutates delete headers, so callers should not expect the original `X-Delete-After` header to remain. `check_utf8('')` returns false, which is correct for names but can surprise generic callers.

## Test signals
Tests should cover config overrides and type conversion, missing/invalid config sections, metadata limit boundaries, header value length, account/container UTF-8 rejection, object creation length and transfer-encoding errors, delete-after/delete-at normalization and replication exception, drive name quoting and mount checks, UTF-8 surrogate/null/reserved-byte behavior, account/container slash rejection, and API-version list coercion.
