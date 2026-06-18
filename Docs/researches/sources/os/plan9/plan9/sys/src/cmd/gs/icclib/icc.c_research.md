# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-9299, source bytes 262143, report `Docs/researches/chunks/chunk_sources_os_plan9_plan9_sys_src_cmd_gs_icclib_icc_c_1_1_9299_b4b6fe720c26_research.md`
- chunk 2: lines 9300-12776, source bytes 100574, report `Docs/researches/chunks/chunk_sources_os_plan9_plan9_sys_src_cmd_gs_icclib_icc_c_2_9300_12776_91d961ca5f49_research.md`

## Chunk Research

### Chunk 1: lines 1-9299

# Chunk Research: sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc.c lines 1-9299

## Scope

This report covers `sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc.c` lines 1-9299 for subset A (`Docs/research_subset_a.md`). The chunk spans the icclib prologue, platform/file/allocator adapters, ICC scalar encoders, string/enumeration helpers, most ICC tag object implementations, LUT interpolation/table-building support, profile header handling, tag/type legality tables, required-tag profile checks, and `icc_read()`. It stops at the `icc_get_size()` declaration; profile writing, tag mutation, lookup-object/color-conversion helpers, normalization functions, color math, and public constructors continue after this chunk.

## Public And Internal APIs Covered

- File abstraction APIs: `new_icmFileStd_fp()`, `new_icmFileStd_name()`, and `new_icmFileMem()` construct `icmFile` vtable objects over `FILE *`, pathname streams, and fixed memory buffers. Their methods are `seek`, `read`, `write`, `flush`, and `del`.
- Allocator abstraction API: `new_icmAllocStd()` creates an `icmAlloc` vtable using `malloc`, `calloc`, `realloc`, and `free`.
- Public utility APIs: `tag2str()`, `str2tag()`, `icm2str()`, `psh_init()`, `psh_reset()`, and `psh_inc()`.
- Scalar conversion helpers read and write ICC big-endian integer/fixed-point encodings: UInt8/16/32/64, SInt32, S15Fixed16, U8Fixed8, U16Fixed16, PCS XYZ/Lab encodings, and normalized device coordinates.
- Tag object methods follow a common `icmBase` shape: `get_size`, `read`, `write`, `dump`, `allocate`, and `del`, with constructors such as `new_icmUInt8Array()`, `new_icmCurve()`, `new_icmLut()`, `new_icmNamedColor()`, and others.
- Tag types implemented in this chunk include numeric arrays, `XYZArray`, `Curve`, `Data`, `Text`, `DateTime`, `Lut8/Lut16`, `Measurement`, `NamedColor/NamedColor2`, `TextDescription`, profile sequence descriptions, `Signature`, `Screening`, `UcrBg`, ColorSync `VideoCardGamma`, `ViewingConditions`, `CrdInfo`, and the 128-byte `icmHeader`.
- LUT APIs on `icmLut` include `nu_matrix`, `min_max`, `lookup_matrix`, `lookup_input`, `lookup_clut_nl`, `lookup_clut_sx`, `lookup_output`, and `set_tables`.
- ICC profile-level APIs covered here are `check_icc_legal()` and `icc_read()`. `icc_get_size()` starts at line 9298 but its body is outside this chunk.

## Control Flow And Behavior

- Standard file objects wrap C stdio directly. `new_icmFileStd_name()` opens the file, adds binary mode via `freopen()` when `O_BINARY` exists, and marks the object to close the stream on deletion. Memory file objects keep `start`, `cur`, and `end` pointers and emulate bounded read/write/seek against the caller-provided buffer.
- Scalar readers/writers centralize ICC on-disk byte order and numeric ranges. Most write helpers return nonzero for unrepresentable values; callers convert that into `icp->err` and `icp->errc`.
- `icm2str()` dispatches an `icmEnumType` selector to specific string conversion helpers for flags, tag signatures, type signatures, color spaces, profile classes, platforms, measurement geometry, rendering intents, spot shapes, observers, illuminants, and lookup algorithms.
- Most tag `read()` functions allocate a temporary file buffer of the tag length, seek to the tag offset, read the tag body, validate the tag type signature, parse fixed fields, allocate variable-sized object storage, decode arrays/strings/curves, then free the temporary buffer.
- Most tag `write()` functions build an in-memory byte buffer from object state, validate representability/null termination where relevant, write the type signature plus reserved padding, then seek and write the whole tag in one call.
- Array tags derive element counts from `(len - header_size) / element_size`. They do not generally reject non-multiple residual bytes; extra trailing bytes are ignored by the derived count.
- `icmCurve_lookup_fwd()` maps normalized input through linear, gamma, or sampled curves. Reverse lookup lazily builds `icmRevTable` bucket lists with `icmTable_setup_bwd()` and uses linear reverse interpolation or nearest-sample fallback.
- `icmLut_lookup_matrix()` applies the 3x3 matrix. `lookup_input()` and `lookup_output()` do per-channel 1D interpolation with clipping flags. `lookup_clut_nl()` performs n-linear interpolation over cube corners, while `lookup_clut_sx()` performs simplex/tetrahedral-style interpolation by sorting coordinate offsets.
- `psh_init()` / `psh_inc()` implement a pseudo-Hilbert, distributed Gray-code traversal used by `icmLut_set_tables()` to populate CLUT vertices in a cache-friendlier multidimensional order.
- `icmLut_set_tables()` chooses normalization functions via `getNormFunc()` (defined after this chunk), builds input tables, CLUT, and output tables from callback transfer functions, supports optional min/max ranges, and has a `SYMETRICAL_DEFAULT_LAB_RANGE` special case for higher-resolution Lab tables.
- `icmLut_read()` accepts either `icSigLut8Type` or `icSigLut16Type`, reads channels, grid points, matrix, table entry counts, allocates input/CLUT/output tables, decodes normalized table values, then computes private `dinc[]` and `dcube[]` offsets for interpolation.
- `NamedColor` parsing has two formats: legacy variable-length root names and 8-bit device coordinates, and `NamedColor2` fixed 32-byte names with PCS XYZ/Lab coordinates and 16-bit device coordinates. It depends on the profile header PCS and device color-space component count.
- `TextDescription` uses `core_read`/`core_write` so nested profile sequence description structs can embed two text descriptions. It parses ASCII, Unicode, and ScriptCode fields, with relaxed minimum length when `ICM_STRICT` is disabled.
- `ProfileSequenceDesc` reads a count, allocates an array of `icmDescStruct`, and each descriptor reads manufacturer/model/attributes/technology followed by device and model text descriptions.
- `icmHeader_read()` reads exactly 128 bytes, decodes profile size, CMM ID, version nibbles, profile class, data color space, PCS, creation date, magic number, platform, flags, manufacturer/model, attributes, rendering intent, illuminant, and creator.
- `check_icc_legal()` consults `tagchecktable[]` to match profile class/channel/color-space/PCS combinations and checks required tag signatures via `p->find_tag()`. It permits alternate rows for some negative channel markers and otherwise returns success once a matching required-tag set is present.
- `icc_read()` stores the caller-supplied `icmFile` and base offset, reads the header, reads the tag count at offset `of + 128`, allocates the tag table, reads all tag records, probes each tag offset for its tag type, and leaves `objp` null so tag objects are read on demand in later code.

## State And Data Structures

- `icc` is the central owner for current file (`fp`), base offset (`of`), allocator (`al`), header, tag table (`data`), tag count, last error string/code (`err`, `errc`), and profile methods referenced in this chunk (`find_tag`).
- `icmBase`-derived tag structs carry `ttype`, `refcount`, method pointers, `icp`, and type-specific payload. Variable allocations cache previous sizes in fields such as `_size`, `_count`, `_channels`, `inputTable_size`, `clutTable_size`, and `outputTable_size`.
- `icmFileStd` owns a `FILE *` plus `doclose`; `icmFileMem` owns buffer bounds and current pointer but does not own the backing memory.
- `icmAllocStd` is a heap allocator object; all ICC object/tag allocations in this chunk are made through `icp->al` except the default file/allocator object constructors themselves.
- `icmCurve` stores a `flag`, `size`, sampled/gamma `data`, and reverse lookup table `rt`.
- `icmRevTable` stores source table metadata, output min/max, quantization scale, bucket lists (`rlists`), and `inited` state for reverse curve/table lookups.
- `icmLut` stores channel counts, CLUT points, input/output entry counts, 3x3 matrix `e`, input/CLUT/output tables, interpolation increments `dinc[]`, cube-corner offsets `dcube[]`, and reverse input/output table caches `rit`/`rot`.
- `icmNamedColor` stores vendor flags, count, device coordinate count, prefix/suffix buffers, and an array of `icmNamedColorVal` entries containing root name, PCS coordinates, and device coordinates.
- `icmTextDescription` stores ASCII, Unicode, and ScriptCode representations plus core read/write hooks. `icmDescStruct` embeds two initialized `icmTextDescription` objects.
- Static dispatch tables in this chunk are `typetable[]` for tag type to object constructor mapping, `sigtypetable[]` for legal tag-signature/tag-type pairings, and `tagchecktable[]` for required tag sets by profile class and color-space constraints.

## Dependencies

- Standard C library dependencies are `stdio.h`, `stdlib.h`, `stdarg.h`, `sys/types.h`, `string.h`, `ctype.h`, `math.h`, and `time.h`, with conditional `unistd.h` for Sun and `float.h` for IBM x86.
- Local interface and type definitions come from `icc.h`; this chunk depends on its ICC signatures/enums, object struct layouts, `MAX_CHAN`, `ORD8/ORD16/ORD32`, `INR8/INR32`, `icmUint64`, `icmInt64`, `icmFile`, `icmAlloc`, `icmBase`, `icc`, and color constants such as `icMagicNumber`.
- Color conversion helpers `icmXYZ2Lab()` and global white point `icmD50` are used in `string_XYZNumber_and_Lab()` before their definitions later in `icc.c`.
- `getNormFunc()` is forward-declared in this chunk and defined after line 9299; `icmLut_set_tables()` cannot work without the later normalization-function table.
- `icc_read()` depends on profile methods initialized outside this range, especially `p->header->read()` and `p->find_tag()`. On-demand tag object reading is handled by later functions after this chunk.
- `sigtypetable[]` is populated here but checked by later add/read/link code outside this chunk.

## Risks And Invariants

- Memory-buffer file I/O treats `(cur + len) >= end` as too much, so full-buffer reads/writes are shortened by one byte. `seek()` also rejects `offset == length`. That is a compatibility/correctness risk for profiles stored in exact-size memory buffers.
- `new_icmFileStd_name()` can leak the originally opened stream if `freopen()` fails after `fopen()` succeeds.
- Many size computations use `unsigned int` and products such as `channels * entries * entrySize`, `outputChan * uipow(clutPoints, inputChan)`, or `count * sizeof(...)` without overflow checks. Malformed profiles can drive undersized allocations or truncated length calculations on 32-bit-style assumptions.
- Several read paths validate only minimum tag size, not exact size or alignment. Array tags ignore residual bytes after integer division, and some structures rely on later per-field bounds checks.
- Some early returns after allocating temporary buffers miss `free()`: for example `icmVideoCardGamma_read()` returns without freeing `buf` when the table payload or formula tag is too short. Its unsupported-entry-size path also calls `pp->del(pp)`, deleting the object while the caller may still own its pointer.
- `icmTextDescription_core_read()` sets `p->size = read_UInt32Number(bp)` before validating the type signature even though `bp` still points at the tag type field; this is later overwritten after the header but is surprising state mutation on malformed data.
- `icmTextDescription_allocate()` allocates exactly `ucSize * sizeof(ORD16)`, but read/write code stores/checks a terminating zero element, so `ucSize` must include the terminator. If a caller supplies a count excluding the terminator, writes can overrun.
- `icmNamedColor_dump()` writes device coordinates with `printf()` instead of the supplied `FILE *op`, so dumps can leak output to stdout rather than the requested stream.
- `icmCrdInfo_write()` tests `if (p->ppsize > 0)` before writing every CRD string; this appears to skip CRD strings when product-name size is zero even if `crdsize[t]` is nonzero.
- Reverse lookup setup divides by `(rmax - rmin)` without a flat-table guard. A constant sampled curve can produce an invalid quantization scale.
- `psh_inc()` uses bit shifts derived from `bits * di`; high dimensionality/resolution can overflow the mask expression. `MAX_CHAN` bounds LUT channels, but resolution is still profile-controlled.
- The code uses static rotating/string buffers for `tag2str()` and flag formatting, and single static buffers for many enum conversions, so these helpers are not thread-safe and nested formatting can overwrite text.
- Header validation checks the magic number and date, but many semantic constraints are deferred or permissive. `check_icc_legal()` ends with "assume anything is ok" when no matching required-tag row fails conclusively.
- Error reporting is centralized through mutable `icp->err`/`errc`; callers must not assume reentrancy or independent error state across shared `icc` objects.

## Cross-Chunk References

- `icc_get_size()` begins at line 9298 and continues in the next chunk. It should be connected to the `DO_ALIGN()` macro and the tag object `get_size()` methods covered here.
- The next chunk should cover `icc_write()`, tag add/link/find/read/rename/unread/delete/read-all/dump/delete methods, and should connect them back to `typetable[]`, `sigtypetable[]`, `check_icc_legal()`, and the lazy `objp == NULL` tag table created by `icc_read()`.
- Normalization functions and lookup-object construction later in the file are required to complete the story for `icmLut_set_tables()` and the LUT lookup methods defined here.
- Later same-file color math defines `icmXYZ2Lab()`, `icmLab2XYZ()`, `icmD50`, `icmD65`, `icmBlack`, Delta-E helpers, chromatic adaptation, and lookup-space/range helpers referenced directly or indirectly by this chunk.
- Public profile constructors near the end of the file must initialize the `icc` method table and header object used by `icc_read()`; this chunk shows their consumers but not their setup.

### Chunk 2: lines 9300-12776

# Chunk Research: sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc.c lines 9300-12776

## Scope

This report covers only `sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc.c` lines 9300-12776 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify the preceding `icc_read()` tag-table loader, the `typetable`/`sigtypetable`/`check_icc_legal()` tables immediately before this chunk, and public struct declarations in `icc.h`.

This is user-space Ghostscript/Argyll ICC color-profile support vendored in the Plan 9 tree. It is in the OS source tree, but this chunk does not implement filesystem, VFS, block, or kernel behavior.

## APIs And Objects

The chunk provides most of the concrete `icc` object methods installed by `new_icc_a()`: profile sizing/writing, tag management, diagnostics/lifetime, lookup creation, and constructors.

It also defines LUT normalization helpers, color-space range lookup, 3x3 matrix helpers, public color utilities (`icmXYZ2Lab()`, `icmLab2XYZ()`, Delta-E helpers), globals (`icmD50`, `icmD65`, `icmBlack`), and lookup implementations for monochrome, matrix/TRC, and multidimensional LUT profiles.

## Control Flow

`icc_write()` validates profile legality, computes aligned layout, writes the header/tag table, and writes each unique tag payload once using `icmBase->touched` to avoid duplicate linked-tag writes.

Tag reading is lazy. `icc_read()` before this chunk populates tag metadata; `icc_read_tag()` creates concrete tag objects on demand via `typetable[]`, links already-loaded matching offset/type/size tags, and calls object-specific `read()`.

Lookup flow is layered: mono uses curve/map/absolute steps; matrix uses curves/matrix/absolute steps; LUT uses input absolute conversion, optional matrix, input tables, CLUT interpolation, output tables, denormalization, and output absolute conversion. Inverse LUT helper components exist for output table, input table, matrix, and absolute conversions, but inverse CLUT is explicitly not implemented.

`icc_get_luobj()` dispatches by ICC profile class, function, intent, PCS override, and preferred search order. Input/display and output profiles can fall back among LUT, matrix, and mono lookup forms. Link, abstract, and colorspace profiles use AToB0/BToA0 LUTs. Named-color lookup is rejected as unimplemented.

## State And Dependencies

Persistent state lives in `icc->header`, `icc->data[]`, `icc->count`, `icc->fp`, `icc->of`, `icc->err`, and `icc->errc`. Allocation goes through `icmAlloc`; tag object lifetime is refcounted through `icmBase->refcount`.

Lookup objects store borrowed pointers to tag objects and cache color spaces, effective PCS, white/black points, chromatic adaptation matrices, normalization callbacks, interpolation callback choice, and lazy inverse caches.

Key dependencies outside this chunk include `check_icc_legal()`, `typetable[]`, `sigtypetable[]`, `new_icmHeader()`, earlier tag constructors, earlier `icmLut` lookup methods, reverse-table helpers, signature helpers, serializers, and standard math/C I/O APIs.

## Risks And Edge Cases

There is a likely double-free in `icc_write()`: after freeing the tag table buffer at line 9450, the flush error path frees `buf` again.

Size calculations use `unsigned int` and `p->count * 12` without visible overflow checks. Large malformed or constructed profiles could wrap layout sizes.

`icc_write()` leaks the tag table buffer on the "corrupted link" path. Most other write error paths free it.

The object model is not thread-safe: profile writing mutates `touched`, lazy reads mutate `objp`/refcounts, and lookup helpers mutate caches and `icc->err`.

Suspicious copy/paste issues are visible: `new_icmLuMono()` assigns public backward component pointers to forward component functions, and `icmLuMatrixBwd_curve()` ignores its `in` parameter because callers already stage data in `out`.

Profile validation is partial, and absolute-colorimetric paths divide by white point components without zero checks.

## Cross-Chunk References

This chunk continues the top-level ICC object implementation after `icc_read()`, which initializes tag-table metadata and leaves tag objects unloaded.

The tag/object factory tables and legality rules used here are defined immediately before the chunk. Earlier chunks define tag type implementations, LUT interpolation, curve lookup, reverse table helpers, file abstractions, allocators, signature helpers, and serializers.

Line 12776 reaches the end separator of the ICC library implementation area. There is no later implementation chunk needed for `icc.c` beyond the compatibility constructor ending at `new_icc()`.
