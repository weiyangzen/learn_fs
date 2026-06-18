# sources/object-store/openstack-swift/swift/common/utils/base.py

## Purpose

`base.py` holds low-level utility functions that other `swift.common.utils` split modules may import without creating circular dependencies. It intentionally imports only standard-library modules and is used by `__init__.py`, logging utilities, CLI code, and request/path parsing code.

## Important APIs, Types, And Functions

- `md5(string=b'', usedforsecurity=True)` wraps `hashlib.md5`, preserving support for Python distributions that accept the `usedforsecurity` keyword while falling back gracefully on distributions that do not.
- `get_valid_utf8_str(str_or_unicode)` accepts bytes or text, decodes invalid UTF-8 with replacement if needed, collapses surrogate pairs through UTF-16 encode/decode, and returns valid UTF-8 bytes.
- `quote(value, safe='/')` URL-quotes values after UTF-8 normalization and returns bytes when the caller passed bytes, preserving legacy behavior.
- `split_path(path, minsegs=1, maxsegs=None, rest_with_last=False)` validates and splits Swift HTTP paths into account/container/object-style segments, padding missing trailing segments with `None`.

## Control Flow And Behavior

At import time, the module probes whether `hashlib.md5(usedforsecurity=False)` is accepted. The successful branch forwards the keyword, while the fallback branch ignores it. This lets Swift use MD5 for non-security storage hashing on FIPS-aware Python builds while retaining older Python compatibility.

`get_valid_utf8_str()` first decodes bytes with `surrogatepass`; on decode failure it uses replacement. It then encodes through UTF-16 with surrogate pass and decodes with replacement to collapse invalid surrogate content before returning UTF-8 bytes. `quote()` feeds those bytes into `urllib.parse.quote` and preserves byte-return behavior for byte input.

`split_path()` enforces a leading slash, minimum and maximum segment counts, and optional "rest with last" behavior for object names containing slashes. It uses `quote(path)` in error messages so invalid or unsafe paths are printable. It rejects empty required segments, rejects extra trailing data unless `rest_with_last` is enabled, and pads the result to the requested maximum segment count.

## State And Persistence

The module has no persistent state. Import-time state is limited to decoder/encoder function objects and the selected `md5` wrapper implementation.

## Dependencies And Integration Points

Dependencies are standard library `codecs`, `hashlib`, and `urllib.parse.quote`. `__init__.py` re-exports all four public helpers. `swift.common.utils.logs` imports `md5`, `quote`, and `split_path`; CLI tools and middleware use `md5` and `split_path`; request parsing throughout account/container/object/proxy paths depends on the exact validation behavior.

## Risks And Edge Cases

- `split_path()` returns a fixed-length list padded with `None`; callers that assume only actual path components may mis-handle optional segments.
- With `rest_with_last=True`, the final returned segment may contain slashes by design.
- The bytes/text preservation in `quote()` is legacy-sensitive; changing return type would break callers that compare or concatenate bytes.
- `get_valid_utf8_str()` intentionally replaces invalid data rather than raising, which is useful for logging/quoting but should not be treated as lossless validation.
- The MD5 wrapper is explicitly for non-security uses. Passing `usedforsecurity=True` on a FIPS-restricted platform can still be rejected by the underlying Python/OpenSSL stack.

## Test Signals

No local test tree is present in this source snapshot. Expected test cases include `md5()` with and without `usedforsecurity` support, invalid UTF-8 and surrogate normalization, `quote()` return type for bytes versus str, and `split_path()` boundary cases for missing leading slash, empty required segments, excessive segments, padded optional segments, and object names containing slash separators.
