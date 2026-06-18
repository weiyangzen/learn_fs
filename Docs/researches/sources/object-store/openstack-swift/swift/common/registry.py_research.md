# sources/object-store/openstack-swift/swift/common/registry.py

## Purpose
`registry.py` is a small process-local registry for cluster capability information and logging redaction metadata. Middleware and subsystems register public and admin-only `/info` data, sensitive headers, and sensitive query parameters; consumers retrieve defensive copies or frozen views.

## Important APIs, types, and functions
`get_swift_info(admin=False, disallowed_sections=None)` returns a deep copy of `_swift_info`, optionally with an `admin` section containing `_swift_admin_info` and the requested disallowed sections. `register_swift_info(name='swift', admin=False, **kwargs)` registers key/value data in either public or admin storage. `get_sensitive_headers()` and `get_sensitive_params()` return frozensets. `register_sensitive_header(header)` lowercases and stores ASCII header names. `register_sensitive_param(query_param)` stores ASCII query parameter names case-sensitively.

## Control flow and state behavior
The module stores mutable process globals: `_swift_info`, `_swift_admin_info`, `_sensitive_headers`, and `_sensitive_params`. Public and admin info are nested by section name. `get_swift_info()` deep-copies public info, then walks dotted disallowed section paths and removes matching leaf keys before optionally attaching admin metadata. Registration rejects reserved section names and any dots in section names or keys, because dots are used only for disallowed-section path traversal.

Sensitive header/param registration validates type and ASCII encodability. Headers are normalized to lower-case for case-insensitive matching; query parameters preserve case.

## Dependencies and integration points
The only import is `copy.deepcopy`. The registry is used by Swift info endpoints and proxy logging redaction. The docstrings reference `swift.common.middleware.proxy_logging`, which reads sensitive header and parameter sets before logging. Middleware such as auth, tempurl, or s3api can register sensitive fields and capability details.

## Risks and edge cases
This is process-local mutable global state, so registrations depend on import/filter initialization order and are not automatically synchronized across worker processes. `get_swift_info()` protects callers from mutating public info by deep-copying, but admin info is copied with `dict()` rather than deep-copied. Dotted disallowed traversal silently ignores missing paths and non-dict intermediates. ASCII validation raises `UnicodeEncodeError`, not a Swift-specific error. Re-registering existing keys overwrites values.

## Test signals
Tests should cover public/admin registration, reserved name rejection, dotted key rejection, deep-copy isolation, disallowed top-level and nested removal, admin disallowed echoing, case normalization for headers, case-sensitive query parameters, non-string type errors, non-ASCII failures, and overwrite behavior.
