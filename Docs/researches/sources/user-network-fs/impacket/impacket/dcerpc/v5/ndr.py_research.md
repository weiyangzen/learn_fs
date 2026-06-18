# sources/user-network-fs/impacket/impacket/dcerpc/v5/ndr.py

## Purpose

`ndr.py` is Impacket's core Network Data Representation serialization runtime for DCE/RPC v5. It provides primitive NDR types, arrays, structures, unions, pointers, top-level calls, NDR64 transfer-syntax switching, referent packing/unpacking, alignment handling, and debug dumping. Most DCE/RPC interface modules in this tree are declarative subclasses of these base classes.

## Important APIs, Types, and Functions

`NDR` is the base field container. It interprets `commonHdr`, `structure`, `referent`, `structure64`, default-value expressions, literal fields, and nested NDR classes. Primitive classes include signed/unsigned small, short, long, hyper, float, double, char, boolean, and `NDRENUM`. `NDRCONSTRUCTEDTYPE` adds pointer/union detection and referent traversal. Array classes include `NDRArray`, `NDRUniFixedArray`, `NDRUniConformantArray`, `NDRUniVaryingArray`, `NDRUniConformantVaryingArray`, `NDRVaryingString`, and `NDRConformantVaryingString`. `NDRSTRUCT` implements structure alignment and conformant-array size relocation. `NDRUNION` implements discriminated arms. `NDRPOINTERNULL`, singleton `NULL`, and `NDRPOINTER` model null, embedded, and top-level pointers. `NDRCALL` serializes complete request/response stubs and aliases to `NDRTLSTRUCT`. `UNKNOWNDATA` captures raw opaque data.

## Control Flow

Construction walks declared fields and creates nested NDR instances, default Python values, byte literals, or lists. `getData` aligns fields, packs primitives with `struct.pack`, delegates nested NDR serialization, and appends referent data for constructed types. `fromString` mirrors the process with alignment, `struct.unpack_from`, array-size extraction, union tag selection, and referent parsing. `changeTransferSyntax` recursively switches objects to NDR64 when the NDR64 UUID is negotiated, replacing headers, structures, alignments, and compatible nested objects. `NDRCALL` treats pointer and union fields as top-level objects so their referents are emitted in the call stub rather than embedded incorrectly.

## State and Persistence Behavior

Objects keep all state in `self.fields`, `_isNDR64`, current `commonHdr`/`structure`, and array-size metadata such as `MaximumCount` or `ActualCount`. Pointers get random nonzero referent IDs by default, so byte-for-byte serialization may vary unless callers set IDs explicitly. No durable state is persisted.

## Dependencies and Integration Points

The module depends on `struct`, `inspect`, `random`, `six`, Impacket logging, Impacket enum support, and UUID conversion. It is the serialization substrate for LSAD, LSAT, MGMT, NRPC, MIMILIB, and other DCE/RPC protocol modules. It also integrates with `rpcrt` through request/response classes mapped by interface `OPNUMS`.

## Risks and Edge Cases

Alignment and conformant-array behavior are complex and easy to regress. The code uses `eval` to compute default field expressions from class declarations, so malformed declarations can fail late or execute expression logic. Pointer null assignment has special behavior that can replace nested `Data` pointers. Union alignment intentionally deviates from a strict reading of the standard based on observed packets. NDR64 support is partial in some paths, with an explicit exception when attempting to switch back from NDR64. Random referent IDs complicate deterministic tests. Python 3 byte/list handling has special cases for char arrays.

## Test Signals

High-value tests are round-trip pack/unpack fixtures for primitives, nested structs, conformant and conformant-varying arrays, arrays of constructed types with referents, top-level versus embedded pointers, null pointers, unions with known/default tags, NDR64 enum and pointer width, and RPC call classes with multiple referents. Regression tests should assert alignment padding length and semantic equality rather than exact random referent IDs.
