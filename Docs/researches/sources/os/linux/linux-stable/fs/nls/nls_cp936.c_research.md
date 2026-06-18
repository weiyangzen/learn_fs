# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp936.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-3984, source bytes 262088, report `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_nls_nls_cp936_c_1_1_3984_ba730d5c32db_research.md`
- chunk 2: lines 3985-8212, source bytes 262119, report `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_nls_nls_cp936_c_2_3985_8212_5ee643007aea_research.md`
- chunk 3: lines 8213-11112, source bytes 174159, report `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_nls_nls_cp936_c_3_8213_11112_8f15402e3205_research.md`

## Chunk Research

### Chunk 1: lines 1-3984

# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp936.c lines 1-3984

## Scope

This chunk is the opening generated data section of the Linux NLS CP936/GB2312 conversion module. It contains the file header, kernel/NLS includes, and the beginning of the CP936 byte-sequence-to-Unicode mapping tables. There is no executable conversion logic in this line range; the runtime APIs are defined later in the same file.

## APIs And Dependencies

- Includes at lines 10-14 pull in module metadata, kernel primitives, string declarations, the NLS registration interface, and errno constants: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`.
- The public API surface is not declared in this chunk. Adjacent downstream context shows these tables feed `page_charset2uni[]` at lines 4389-4422, then `char2uni()` at lines 11049-11085, and module registration through `struct nls_table` at lines 11088-11095.
- All symbols in this chunk are `static const wchar_t`, so they are translation-unit-local read-only lookup data. They become externally relevant only through the later `page_charset2uni` pointer table and the NLS callbacks.

## Data Tables

- Lines 16-3972 define complete `c2u_XX[256]` tables for CP936 lead bytes `0x81` through `0xF0`.
- Lines 3974-3984 start `c2u_F1[256]` and stop mid-definition; the rest of `c2u_F1` is in the next chunk.
- The line range contains 28,160 parsed `0xNNNN` entries, 19,885 of them nonzero. `0x0000` is used as an invalid/unmapped sentinel in these tables, not as a valid Unicode result for double-byte CP936 mappings.
- Main risk is table correctness: manual edits or lead-byte dispatch misalignment in later chunks would silently corrupt filename transcoding.

## Control Flow And State

No function bodies or branches appear in lines 1-3984. Downstream `char2uni()` indexes `page_charset2uni[ch]`, reads `charset2uni[cl]`, rejects `0x0000` as `-EINVAL`, and returns valid two-byte mappings.

The chunk has no mutable state, allocation, locking, reference counting, or I/O. It is static read-only kernel data.

## Cross-Chunk References

- Next chunk continues `c2u_F1` and defines remaining `c2u_F2` through `c2u_FE`, plus `page_charset2uni[256]`.
- Later chunks define reverse `u2c_XX[512]` tables and `page_uni2charset[256]`.
- Final logic appears near file end: `uni2char()`, `char2uni()`, `struct nls_table table`, module init/exit, and module metadata.

### Chunk 2: lines 3985-8212

# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp936.c lines 3985-8212

## Scope

This chunk is the middle generated data section of the Linux NLS CP936/GB2312 conversion module. It completes the byte-sequence-to-Unicode table that began in the previous chunk, defines the forward dispatch table used by `char2uni()`, and then begins the Unicode-to-CP936 reverse mapping table corpus used by `uni2char()`.

There are no function bodies in this line range. Runtime behavior is indirect: later conversion callbacks index the static tables defined or referenced here.

## APIs And Dependencies

- No callable API is defined in this chunk.
- `page_charset2uni[256]` at lines 4389-4422 is the key internal dispatch structure for later `char2uni()`. It maps CP936 lead-byte values `0x81` through `0xFE` to `c2u_XX[256]` arrays and leaves unsupported lead bytes as `NULL`.
- `u2c_XX[512]` tables starting at line 4424 are reverse lookup pages for later `uni2char()`. Each Unicode page table stores two output bytes per low-byte index, so lookup uses `cl * 2` and `cl * 2 + 1` in the later callback.
- The table definitions depend on `wchar_t`, `unsigned char`, and `NULL` declarations from earlier includes in the same translation unit. Later chunks depend on these symbols when constructing `page_uni2charset[256]` and the Linux `struct nls_table`.

## Data Tables

- Lines 3985-4008 finish `c2u_F1[256]`, whose declaration and first entries are in chunk 1.
- Lines 4010-4387 define `c2u_F2[256]` through `c2u_FE[256]`, completing the forward CP936 lead-byte tables.
- Lines 4389-4422 define `page_charset2uni[256]`.
- Lines 4424-8212 define full `u2c_00` through selected Unicode pages up to `u2c_79`, then start `u2c_7A[512]`.
- The range contains 61 `u2c_XX[512]` declarations and 13 `c2u_XX[256]` declarations, plus one forward dispatch table.

## Control Flow And State

This chunk has no local control flow, branching, allocation, locking, I/O, or mutable state. Every object is `static const`, so the chunk contributes read-only translation-unit-local lookup data.

Effective control flow appears only in consumers outside this chunk: later `char2uni()` reads `page_charset2uni[ch]`, while later `uni2char()` reads `page_uni2charset[ch]` and the `u2c_XX` tables defined here.

## Risks And Edge Cases

- `0x0000` in `c2u_*` and `0x00, 0x00` in `u2c_*` are unmapped sentinels; accidental edits can silently corrupt conversion behavior.
- Dispatch alignment is fragile: `page_charset2uni[0xF1]` must point to `c2u_F1`, `0xFE` to `c2u_FE`, and `0xFF` must remain `NULL`.
- Chunk boundaries split active tables: this chunk starts mid-`c2u_F1` and ends mid-`u2c_7A`.
- Reverse tables encode two bytes per Unicode code point, so byte order must be preserved exactly.
- Sparse pages contain many zero pairs by design.

## Cross-Chunk References

- Chunk 1 declares `c2u_81` through `c2u_F0` and begins `c2u_F1`; this chunk completes `c2u_F1` and adds `c2u_F2` through `c2u_FE`.
- This chunk’s `page_charset2uni` references all `c2u_81` through `c2u_FE` tables, including arrays declared in chunk 1.
- Chunk 3 continues `u2c_7A`, defines remaining reverse tables, builds `page_uni2charset[256]`, and defines the executable NLS callbacks and module metadata.

### Chunk 3: lines 8213-11112

# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp936.c lines 8213-11112

## Scope

This chunk covers lines 8213-11112 of `sources/os/linux/linux-stable/fs/nls/nls_cp936.c` for `learn_fs` subset A. It starts at the tail of `u2c_7A`, contains the remaining Unicode-to-CP936 byte-pair tables, defines the Unicode page dispatch table and ASCII-only case maps, and ends with the NLS conversion callbacks plus module registration metadata.

The file is an automatically generated CP936/GB2312 translation table with a small handwritten-looking wrapper around Linux's NLS API. This chunk is the only visible part of the requested range that contains executable control flow.

## APIs And Entry Points

- `uni2char()` converts one Unicode code point to one or two CP936 bytes.
- `char2uni()` converts one CP936 byte sequence to one Unicode code point.
- `table` advertises charset `"cp936"`, alias `"gb2312"`, conversion callbacks, and byte-wise case maps.
- `init_nls_cp936()` registers the table with `register_nls(&table)`.
- `exit_nls_cp936()` unregisters it with `unregister_nls(&table)`.
- Module macros expose initialization, exit, description, license, and `gb2312` NLS alias metadata.

## Data Layout

The chunk contains `u2c_*[512]` tables for Unicode high-byte pages `0x7B` through `0x9F`, plus sparse pages `0xDC`, `0xF9`, `0xFA`, `0xFE`, and `0xFF`. It also begins with the final bytes of `u2c_7A`, declared in the previous chunk. Each table stores 256 two-byte CP936 results indexed as `low_byte * 2`; `0x00, 0x00` marks an unmapped Unicode code point.

`page_uni2charset[256]` maps Unicode high bytes to these `u2c_*` tables or `NULL`. `charset2lower[256]` and `charset2upper[256]` only fold ASCII letters; bytes `0x80-0xff` are identity-preserved.

## Control Flow

`uni2char()` rejects `boundlen <= 0`, special-cases `U+20AC` to byte `0x80`, handles Unicode page `0x00` through `u2c_00` with ASCII fallback, and otherwise dispatches through `page_uni2charset[ch]`. Missing pages or `0x00, 0x00` entries return `-EINVAL`; insufficient output space returns `-ENAMETOOLONG`.

`char2uni()` rejects empty input, decodes one-byte input directly with a `0x80 -> U+20AC` exception, and for two-byte input dispatches through `page_charset2uni[ch]`. If a lead-byte table exists and the second byte is nonzero, a zero Unicode result is invalid. Otherwise it falls back to single-byte decoding.

## State And Dependencies

All local state is immutable static data. There is no allocation, locking, or per-instance state.

Dependencies include earlier `c2u_*` tables and `page_charset2uni[256]`, earlier `u2c_*` tables such as `u2c_00`, Linux NLS APIs from `<linux/nls.h>`, errno values from `<linux/errno.h>`, and module infrastructure from `<linux/module.h>`.

## Risks And Edge Cases

- Malformed two-byte input with a missing lead-byte table may be consumed as one byte rather than rejected.
- A zero second byte disables two-byte decoding and falls back to single-byte decoding.
- `U+0000` can encode as byte `0x00`; callers must not assume output is NUL-free.
- Generated `0x00, 0x00` sentinels are semantically meaningful and fragile to manual edits.
- Case conversion is byte-local and ASCII-only, not multibyte-aware.

## Cross-Chunk References

- This chunk starts inside `u2c_7A`; its declaration and most entries are in the previous chunk.
- `char2uni()` depends on `page_charset2uni` and `c2u_*` arrays declared before this chunk.
- `uni2char()` depends on earlier `u2c_*` arrays and the tables completed here.
- This chunk closes the source file; the final per-file report should merge earlier generated table context with this chunk’s callback and module-registration behavior.
