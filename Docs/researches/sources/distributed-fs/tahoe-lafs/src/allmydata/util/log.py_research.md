# sources/distributed-fs/tahoe-lafs/src/allmydata/util/log.py

## Purpose

This module wraps Foolscap logging for Tahoe, preserving log level constants, converting bytes in keyword fields to JSON-safe Unicode, and providing mixins that maintain parent message IDs and optional instance prefixes.

## APIs and control flow

`msg()` delegates to `foolscap.logging.log.msg()` after converting kwargs with `jsonbytes.bytes_to_unicode(any_bytes=True)`. `err()` also reports to Twisted's legacy log so unit tests fail on unexpected errors, sets a default `UNUSUAL` level, then delegates to Foolscap. `LogMixin` stores facility and parent/grandparent message IDs; `log()` chooses the parent, coerces kwarg names to native strings, records the first message id as parent, and returns the new id. `PrefixingLogMixin` combines `nummedobj.NummedObj` identity with `LogMixin` and prepends an instance prefix.

## State, dependencies, risks, and tests

State is per-instance parent message id and prefix. Dependencies are Foolscap logging, Twisted logging, pyutil `nummedobj`, `six.ensure_str`, and `jsonbytes`.

Risks include bytes conversion changing structured log values, `err()` making tests fail for handled errors if callers choose the wrong API, and parent message id state causing surprising log hierarchy after the first call. Test signals should cover bytes kwargs, default/error levels, Twisted error forwarding, parent/grandparent behavior, prefix construction from bytes, and first-message parent retention.
