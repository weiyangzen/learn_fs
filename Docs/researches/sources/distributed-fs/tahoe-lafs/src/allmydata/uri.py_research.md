# sources/distributed-fs/tahoe-lafs/src/allmydata/uri.py

## Purpose

This module defines Tahoe-LAFS capability URI objects and parsers. It covers immutable CHK caps, literal caps, mutable SSK and MDMF read/write/verifier caps, directory wrappers around those file caps, unknown-cap handling, Twisted adapter registration, and URI-extension packing. The classes still use historical `to_string()` naming even though the values are bytes.

## APIs and control flow

Important types are `CHKFileURI`, `CHKFileVerifierURI`, `LiteralFileURI`, `WriteableSSKFileURI`, `ReadonlySSKFileURI`, `SSKVerifierURI`, `WriteableMDMFFileURI`, `ReadonlyMDMFFileURI`, `MDMFVerifierURI`, directory URI variants, directory verifier variants, and `UnknownURI`. Each concrete cap has a `BASE_STRING`, regex parser, `init_from_string()`, `to_string()`, readonly/mutable predicates, and methods for deriving readonly or verifier caps. `wrap_dirnode_cap()` maps a file cap to the corresponding directory cap.

`from_string()` is the dispatcher. It accepts unicode or bytes, strips `ro.` and `imm.` alleged-constraint prefixes, enforces readonly or deep-immutable context rules, and returns either a concrete cap or `UnknownURI` with an attached `MustBeReadonlyError`, `MustBeDeepImmutableError`, or `BadURIError`. The `from_string_*` helpers assert interface conformance and are registered as adapters for bytes.

## State, dependencies, risks, and tests

State is object-local key material, storage indexes, fingerprints, share counts, and sizes. Persistent compatibility is the serialized cap bytes; changing regexes, field order, hash derivations, or prefixes can invalidate existing files. Dependencies include `base32`, `hashutil`, storage index conversion helpers, `allmydata.interfaces`, Twisted adapters, and zope interfaces.

Risks include accepting malformed prefixes as unknown instead of failing loudly, regexes that intentionally allow some trailing MDMF separators, assertion-based validation in adapter helpers, and the security sensitivity of readonly/deep-immutable constraints. URI-extension packing sorts keys, netstring-encodes values, coerces selected values back to ints, and hashes readable output; callers depend on deterministic bytes. Test signals should cover round-trips for every cap class, readonly and immutable constraint failures, unknown/future cap prefixes, adapter registration, literal-cap edge cases, verifier derivation, and `pack_extension`/`unpack_extension` compatibility.
