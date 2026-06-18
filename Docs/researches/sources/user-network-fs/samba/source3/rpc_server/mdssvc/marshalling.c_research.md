# sources/user-network-fs/samba/source3/rpc_server/mdssvc/marshalling.c

## Purpose
This file packs and unpacks mdssvc Spotlight RPC binary values between `DALLOC_CTX` typed trees and on-wire Spotlight query/reply blobs. It implements the tag, table-of-contents, endian, string, date, numeric, UUID, CNID, array, dictionary, and file metadata handling used by Samba's Spotlight metadata server.

## Important APIs, Types, And Functions
Public APIs are `sl_pack_alloc()` and `sl_unpack()`. Internal constants define Spotlight primitive and complex tag types, maximum table-of-contents and command sizes, and the Spotlight epoch delta. `struct sl_tag` is the decoded 64-bit tag view with `type`, `count`, `length`, and `size`. Packing helpers include `sl_pack_tag()`, `sl_pack_uint64()`, `sl_pack_uint64_array()`, `sl_pack_bool()`, `sl_pack_nil()`, `sl_pack_float()`, `sl_pack_date()`, `sl_pack_uuid()`, `sl_pack_CNID()`, `sl_pack_array()`, `sl_pack_dict()`, `sl_pack_filemeta()`, `sl_pack_string()`, `sl_pack_string_as_utf16()`, `sl_pack_loop()`, and `sl_pack()`. Unpacking helpers include `sl_unpack_tag()`, `sl_unpack_ints()`, `sl_unpack_date()`, `sl_unpack_uuid()`, `sl_unpack_floats()`, `sl_unpack_CNID()`, `sl_unpack_cpx()`, and `sl_unpack_loop()`.

## Control Flow
Packing starts in `sl_pack_alloc()`, which allocates a bounded blob and calls `sl_pack()`. `sl_pack()` reserves the 16-byte header, recursively packs data elements starting at offset 16, builds complex object ToC entries in a side buffer, writes the little-endian marker `"432130dm"`, writes octet counts, appends the ToC tag and entries, then records blob length. `sl_pack_loop()` dispatches by dalloc type name and writes primitive tags inline while complex values write a complex reference plus a ToC entry.

Unpacking starts in `sl_unpack()`, detects byte order from the first 8 bytes, reads header octet counts, validates total/data/ToC bounds, decodes the ToC tag, then calls `sl_unpack_loop()` for the root object. Primitive tags add typed values to the output dalloc tree. Complex tags look up their ToC entry and call `sl_unpack_cpx()` to construct nested arrays, dictionaries, strings, UTF-16 strings, file metadata, or CNID structures.

## State And Persistence
All state is transient and talloc-owned. Packed blobs are written to `struct mdssvc_blob`; unpacked values are appended into a caller-provided `DALLOC_CTX`. The only persistent semantic conversion is between Unix time and Spotlight's 2001 epoch for date values.

## Dependencies And Integration Points
The implementation depends on Samba byte-order macros, debug logging, charset conversion, `dalloc`, `marshalling.h`, `mdssvc_blob`, and talloc. It is a core integration point between mdssvc RPC handlers and the higher-level dalloc representation consumed by query and metadata logic.

## Risks And Test Signals
Risks include binary parser attack surface, reliance on dalloc type-name strings, mixed use of bytes and 8-byte octets, hardcoded little-endian packing, unsupported big-endian UTF-16 strings, length/count overflow mistakes, recursive unpacking of nested file metadata, and fixed maximum string/ToC/count limits that may reject valid clients or hide edge bugs. Test signals should include pack/unpack round trips for every supported type, malformed headers, endian markers, oversized counts/lengths, ToC index bounds, UTF-8 and UTF-16 strings with BOMs, dates with fractional seconds, empty and non-empty CNID arrays, nested dictionaries/arrays/filemeta, max fragment behavior, and fuzzing of `sl_unpack()`.
