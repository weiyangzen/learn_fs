# sources/distributed-fs/tahoe-lafs/src/allmydata/util/cbor.py

## Purpose

This module is a deliberate CBOR entry point that allows encoding through `cbor2` but blocks decoding through the wrong library. Tahoe-LAFS wants CBOR decoding to use `pycddl`, presumably for schema validation and safer decoding behavior.

## APIs and control flow

`dumps` and `dump` are imported directly from `cbor2`. `load()` always raises `RuntimeError("Use pycddl for decoding CBOR")`, and `loads` is an alias to that rejecting function. `__all__` exports all four names so accidental imports still get a loud failure for decoding.

## State, dependencies, risks, and tests

There is no state or persistence here; persistence belongs to callers that serialize CBOR bytes. The only dependency is `cbor2` for encoding. The main integration point is policy: modules should use this file instead of importing `cbor2.loads()`.

Risks are bypassing this module and decoding without pycddl, or assuming `loads` works because it is exported. Test signals should verify `dump`/`dumps` can encode representative values and `load`/`loads` raise consistently with the exact guidance message.
