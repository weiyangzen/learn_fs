# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_uri.py

## Purpose
This module validates Tahoe-LAFS capability URI objects and parsing helpers. It covers literal files, immutable CHK files and verifier caps, URI extension packing, unknown/future caps, cap constraints, mutable SSK and MDMF file caps, and directory caps built on those file caps.

## Important APIs, Types, And Functions
The tests exercise `uri.LiteralFileURI`, `uri.CHKFileURI`, `uri.CHKFileVerifierURI`, `uri.WriteableSSKFileURI`, `uri.ReadonlySSKFileURI`, `uri.SSKVerifierURI`, `uri.WriteableMDMFFileURI`, `uri.ReadonlyMDMFFileURI`, `uri.MDMFVerifierURI`, `uri.DirectoryURI`, `uri.ReadonlyDirectoryURI`, `uri.ImmutableDirectoryURI`, `uri.LiteralDirectoryURI`, `uri.MDMFDirectoryURI`, `uri.ReadonlyMDMFDirectoryURI`, and directory verifier types. Parser and helper coverage includes `uri.from_string`, `from_string_mutable_filenode`, `from_string_verifier`, `is_uri`, `is_literal_file_uri`, `has_uri_prefix`, `pack_extension`, `unpack_extension`, `unpack_extension_readable`, and `get_readonly`/`get_verify_cap`.

## Control Flow
Each class builds representative caps from deterministic byte strings and validates interface provision (`IURI`, `IFileURI`, `IDirnodeURI`, `IMutableFileURI`, `IVerifierURI`), mutability/read-only flags, storage indexes, sizes, encoded strings, equality, hashing, and attenuation paths. Deep-immutable parsing is checked for immutable caps and deliberately rejected for mutable write/read caps by returning `UnknownURI`. MDMF tests verify writecap-to-readcap-to-verifycap derivation, type-specific parser rejection, and tolerance of future extension fields.

Directory tests wrap file caps in directory cap types and verify filenode cap extraction, read-only attenuation, verifier cap shape, literal directory behavior with no verifier/storage index, immutable directory preservation under deep-immutable parsing, and MDMF directory verifier stability through attenuation.

## State And Persistence
The module has no persistent state. It constructs deterministic in-memory keys, fingerprints, hashes, URI strings, and random extension suffixes. All assertions are pure object/serialization round trips except for use of `os.urandom` to demonstrate opaque future extension tolerance.

## Dependencies And Integration Points
The module depends on `allmydata.uri`, `hashutil`, `base32`, Tahoe interface definitions, `CapConstraintError`, and `ReallyEqualMixin`. It is a direct compatibility suite for cap serialization, cap attenuation, future-cap handling, and parser behavior used by web, CLI, node creation, mutable file, immutable file, and directory layers.

## Risks And Test Signals
The tests strongly signal regressions in capability wire formats, equality/hash behavior, read-only/verifier attenuation, unknown-cap preservation, interface implementation, and parser dispatch. Risks include heavy reliance on fixed byte encodings and limited coverage of malformed strings beyond selected constructor errors and one constraint case. The future-extension tests are important because overly strict parsers would break forward compatibility.
