# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctf_api.h

Private libctf and kernel CTF module API. It exposes opaque CTF container/type handles, libctf-specific error codes, section descriptors, type metadata structs, iteration callback signatures, open/query/update/write routines, and dynamic type construction APIs.

Key elements:
- Explicitly warns that the interface is not public and may change between releases.
- Defines opaque `ctf_file_t` and `ctf_id_t`, plus `CTF_ERR` for failed ID/status returns.
- Enumerates libctf error codes starting at `ECTF_BASE`, covering format, ELF/CTF version, endian, symbol/string table, corruption, missing data, parent/model mismatch, mmap/zlib/decompression, bad names/IDs, wrong type kind, missing labels/members/enums, read-only/full/dynamic conflicts, merge/label conflicts, and conversion backend errors.
- `ctf_sect_t` describes raw CTF, symbol, and string table buffers for `ctf_bufopen()`.
- Defines public query structs for encodings, member info, array info, function info, and label info.
- Defines CTF data-model constants and `CTF_MODEL_NATIVE`.
- Defines dynamic-container add flags for root and non-root type visibility.
- Callback typedefs support visits over type graphs, members, enums, types, labels, functions, objects, and strings.
- Opening APIs support buffers, file descriptors, paths, dynamic creation, fd-backed creation, duplication, close, parent metadata, import, data-model get/set, and per-container private data.
- Query APIs cover errors, flags, version, max type id, symbol count, function info/args, lookup by name or symbol, symbol name, type resolution/naming/size/alignment/kind/reference/pointer/encoding/visit/compare/compatibility, member/array/enum/label info, and iterators.
- Dynamic update APIs add arrays, qualifiers, enums, floats, forwards, function pointers, integers, pointers, imported types, typedefs, structs/unions, enumerators, members, function/object/label records, set array/root/size, delete types, update/discard/write, and expose raw data pointers.
- Kernel-only API includes `ctf_modopen()` for opening CTF data from a loaded module.

Dependencies:
- Includes `sys/elf.h` and `sys/ctf.h`, and uses ELF section constants and CTF format/type definitions.
- Shared by userland libctf consumers and kernel CTF support, with kernel-specific declarations guarded by `_KERNEL`.

Research notes:
- The API intentionally separates immutable container inspection from dynamic container mutation and requires `ctf_update()`/`ctf_discard()` to commit or abandon edits.
- Many callbacks return `int`, implying iteration can be stopped or failed by the callback implementation.
- Type IDs are opaque at the API level even though `ctf.h` documents their on-disk encoding.
