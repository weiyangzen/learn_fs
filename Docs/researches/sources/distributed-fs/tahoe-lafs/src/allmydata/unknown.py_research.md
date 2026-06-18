# sources/distributed-fs/tahoe-lafs/src/allmydata/unknown.py

## Purpose

This module represents filesystem nodes whose capability type is not understood by the current Tahoe-LAFS code. It preserves security constraints around read/write authority and immutable-directory membership while allowing unknown read-only or alleged-immutable caps to be stored and copied when safe.

## Important APIs, types, and functions

- `strip_prefix_for_ro(ro_uri, deep_immutable)` removes `ALLEGED_READONLY_PREFIX` or, in deep-immutable contexts, `ALLEGED_IMMUTABLE_PREFIX` from a URI before storage in an `ro_uri` slot.
- `UnknownNode` implements `IFilesystemNode`.
- `UnknownNode.__init__(given_rw_uri, given_ro_uri, deep_immutable=False, name=u"<unknown name>")` validates byte inputs, normalizes falsey caps to `None`, records errors instead of raising immediately, and decides whether to store an rw cap, ro cap, or an opaque error node.
- `get_cap()` and `get_readcap()` return `uri.UnknownURI` wrappers for the best cap or read cap.
- `is_readonly()` and `is_mutable()` raise `AssertionError` because unknown nodes cannot safely answer those questions.
- `is_unknown()` returns `True`.
- `is_allowed_in_immutable_directory()` returns true only for non-error nodes without an rw URI.
- `is_alleged_immutable()` returns true for non-error, read-only-only nodes whose ro URI is absent or alleged immutable.
- `raise_error()` raises the stored validation error if present.
- Filesystem-node methods such as `get_uri`, `get_write_uri`, `get_readonly_uri`, `get_current_size`, `check`, and `check_and_repair` expose available caps or neutral succeeded-Deferred results.
- Equality compares `rw_uri` and `ro_uri` for other `UnknownNode` instances.

## Control flow

Construction is the critical control flow. If an rw URI is provided in a deep-immutable context, the constructor only accepts it when it is actually an alleged immutable cap and no ro URI was provided; otherwise it records `MustNotBeUnknownRWError` or `MustBeDeepImmutableError` and returns an opaque node. Outside deep-immutable mode, a single unprefixed cap in the rw slot is rejected because it might carry write authority that cannot be diminished. A single cap already prefixed as readonly or immutable is moved to the ro slot. A pair of rw and alleged-immutable ro caps is rejected as inconsistent.

If a ro URI remains, the constructor asks `uri.from_string(..., deep_immutable=deep_immutable, name=name)` to validate constraints. If parsing yields an `UnknownURI` with an error, the node stays opaque and stores that error. Otherwise the constructor strengthens stored caps: in deep-immutable mode it ensures the ro URI has `ALLEGED_IMMUTABLE_PREFIX`; in mutable-directory mode it stores the rw URI if any and ensures the ro URI has at least an alleged readonly/immutable prefix.

## State and persistence behavior

An `UnknownNode` stores only three pieces of local state: `error`, `rw_uri`, and `ro_uri`. It has no storage index, verify cap, repair cap, size, repair/check behavior, or persistence layer. Check operations return succeeded Deferreds with `None`, reflecting that unknown nodes cannot be checked by this implementation.

## Dependencies and integration points

The module depends on `zope.interface.implementer`, Twisted Deferred helpers, `IFilesystemNode`, `MustNotBeUnknownRWError`, `MustBeDeepImmutableError`, URI parsing/`UnknownURI`, and alleged readonly/immutable URI prefixes from `allmydata.uri`. It integrates with directory/node creation paths that may encounter future or unsupported capability types while preserving WebAPI/directory security rules. Tests in the web suite exercise unknown cap linking and immutable-directory child validation.

## Risks and edge cases

- The constructor intentionally delays errors by storing them, so callers must remember to call `raise_error()` or inspect permission methods when attaching nodes.
- Calling `is_readonly()` or `is_mutable()` is a bug and raises by design.
- Prefix handling is security-sensitive: adding a readonly or immutable prefix is only allowed after enough context establishes that the cap should not be treated as write authority.
- Single unprefixed unknown caps are rejected to avoid accidental write-authority leakage.
- Deep-immutable mode treats alleged immutable prefixes as constraints, not proof of real immutability.

## Test signals

Relevant signals include unknown rw cap rejection in write slots, unknown readonly and alleged immutable caps linking successfully, immutable directory creation rejecting mutable/unknown rw children, and round-tripping of unknown ro/immutable caps through directory JSON or child assertions. Direct unit coverage should focus on constructor matrix cases, prefix stripping/strengthening, delayed errors, and `is_allowed_in_immutable_directory`.
