# sources/user-network-fs/samba/source4/torture/ndr/cabinet.c

## Purpose
`cabinet.c` tests Samba's generated NDR parser for Microsoft Cabinet (`cab_file`) structures. It embeds three complete CAB fixtures: an uncompressed cabinet containing a 32 KiB file of `A` bytes, an MSZIP-compressed version of the same logical file, and an LZX-compressed version. The tests verify header fields, folder/file metadata, data block sizes and checksums, and decompressed content where the implementation supports it.

## Important APIs, types, and functions
- `cab_file_plain_data` is a large static fixture for a `MSCF` cabinet with `CF_COMPRESS_NONE`. Most of the file's 4,335 lines are the 32 KiB literal `A` payload in this array.
- `cab_file_MSZIP_data` is a compact fixture for the same 32 KiB logical file using `CF_COMPRESS_MSZIP`.
- `cab_file_LZX_data` is a compact fixture for the same logical file using LZX compression; the code currently checks metadata but leaves decompressed payload validation disabled.
- `cab_file_plain_check`, `cab_file_MSZIP_check`, and `cab_file_LZX_check` validate the parsed `struct cab_file` fields.
- `ndr_cabinet_suite(TALLOC_CTX *ctx)` registers the cabinet subtests through `torture_suite_add_ndr_pull_test` and one plain round-trip validation via `torture_suite_add_ndr_pull_validate_test`.

## Control flow
The suite registers three pull-only tests, one for each fixture. The shared NDR harness pulls the fixture into `struct cab_file` using generated functions from `librpc/gen_ndr/ndr_cab.h`, then invokes the corresponding check function. The check functions assert the `MSCF` signature, cabinet size, file-table offset, version, folder count, file count, flags, set/cabinet identifiers, folder data offset, number of data blocks, compression type, file size, file offset, folder index, DOS date/time, attributes, filename, data-block checksum, compressed byte count, and uncompressed byte count. For plain and MSZIP fixtures, they allocate a `DATA_BLOB` of 0x8000 bytes, fill it with `A`, and compare it to `r->cfdata[0].ab`. For LZX, the equivalent payload comparison is inside `#if 0` because LZX decompression support is not enabled.

The suite also registers a pull/push validation for the plain fixture. The MSZIP validate test is intentionally commented out because zlib can produce a different but equivalent compressed stream, making byte-for-byte round-trip validation unsuitable for that fixture.

## State and persistence behavior
There is no persistent state. Static fixture arrays are read-only. Check functions allocate temporary `DATA_BLOB` objects using Samba allocation helpers, fill them with deterministic content, compare them, and free them before returning.

## Dependencies and integration points
The file depends on the generic Samba torture/NDR harness, generated Cabinet NDR declarations in `ndr_cab.h`, and constants such as `CF_COMPRESS_NONE` and `CF_COMPRESS_MSZIP`. It is added to the parent NDR test suite by `ndr.c` through `ndr_cabinet_suite(suite)`. The implementation under test is the generated `ndr_pull_cab_file`/`ndr_push_cab_file` path and any Cabinet decompression support it invokes for `cfdata[0].ab`.

## Risks and edge cases
- The enormous plain fixture makes reviews noisy and increases the chance of accidental fixture corruption.
- LZX content validation is explicitly disabled, so the LZX test currently proves header/data-block parsing but not successful decompression.
- MSZIP push validation is disabled because compression output is not byte-stable across zlib behavior; this is intentional but leaves round-trip coverage weaker for compressed cabinets.
- The tests cover a simple one-folder, one-file cabinet only. Multi-folder, multi-file, continuation cabinet, reserved-area, and malformed checksum paths are not represented.
- The LZX check uses the numeric value `4611` for `typeCompress` rather than a named constant, which is less self-documenting and can hide enum/bitfield intent.

## Test signals
Passing tests demonstrate that Samba parses basic CAB headers, CFFOLDER/CFFILE tables, CFDATA metadata, uncompressed data, and MSZIP decompressed data for a deterministic 32 KiB payload. The plain validation subtest additionally proves byte-for-byte pull/push stability for an uncompressed cabinet.
