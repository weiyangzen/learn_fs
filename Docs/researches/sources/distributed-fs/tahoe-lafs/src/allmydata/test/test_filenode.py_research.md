# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_filenode.py

Purpose: tests public behavior of Tahoe file node classes for immutable CHK files, literal files, and mutable SSK files. It verifies equality, hashing, capability accessors, read/write/verify/repair cap behavior, mutability/read-only flags, storage indexes, literal downloads, and checker behavior for literal nodes.

Important APIs and types include `NotANode`, `FakeClient`, `Node`, and `LiteralChecker`. The implementation under test includes `ImmutableFileNode`, `LiteralFileNode`, `MutableFileNode`, URI classes such as `CHKFileURI`, `LiteralFileURI`, and `WriteableSSKFileURI`, `hashutil.ssk_*` helpers, `download_to_data`, and `Monitor`.

Control flow constructs cap objects directly instead of creating a grid. The CHK test instantiates two `ImmutableFileNode` objects from the same CHK URI and checks identity semantics and derived verifier/repair caps. The literal test constructs a literal URI, downloads all bytes and a slice, asks for best readable version and size, and checks that literal nodes have no storage index or repair cap. Mutable tests derive readkey and storage index from a writekey, initialize nodes from writeable and readonly SSK caps, and check equality/hash replacement in dictionaries and readonly projection behavior.

State and persistence are in-memory only. `FakeClient` supplies minimal encoding parameters, broker/history placeholders, and a `SecretHolder` sufficient for mutable node initialization. Literal downloads use memory consumers and do not create shares or storage directories.

Dependencies include Twisted Trial, Tahoe URI and client secret-holder code, immutable and mutable filenode implementations, hash utilities, `Monitor`, and the consumer helper. Integration points are the file node interface expected by directories, web/API download helpers, repair/check APIs, and capability conversion semantics.

Risks covered include confusing nodes with raw URI objects or unrelated types, incorrect readonly/write URI exposure, mutable readonly nodes accidentally exposing repair/write capabilities, bad equality/hash semantics causing cache or dict collisions, literal ranged reads, and CHK verify-cap derivation. Residual risk is that networked immutable/mutable operations are not covered here; these tests focus on object API contracts.

Test signals include exact URI byte strings from accessors, boolean capability flags, storage index derivation, dictionary key replacement for equal mutable nodes, successful literal downloads and slices, and `LiteralFileNode.check` returning `None` for both normal and verify checks.
