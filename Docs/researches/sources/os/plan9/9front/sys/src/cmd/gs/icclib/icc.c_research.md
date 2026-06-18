# File Research: sources/os/plan9/9front/sys/src/cmd/gs/icclib/icc.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-9299, source bytes 262143, report `Docs/researches/chunks/chunk_sources_os_plan9_9front_sys_src_cmd_gs_icclib_icc_c_1_1_9299_097a14b7666f_research.md`
- chunk 2: lines 9300-12776, source bytes 100576, report `Docs/researches/chunks/chunk_sources_os_plan9_9front_sys_src_cmd_gs_icclib_icc_c_2_9300_12776_a01e27881288_research.md`

## Chunk Research

### Chunk 1: lines 1-9299

# Chunk Research: sources/os/plan9/9front/sys/src/cmd/gs/icclib/icc.c lines 1-9299

## Scope

This report covers only `sources/os/plan9/9front/sys/src/cmd/gs/icclib/icc.c` lines 1-9299 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only from `icc.h` to identify the public structs, method-pointer interfaces, and type names implemented by this chunk. This is user-space ICC profile parsing, writing, dumping, and color-table support inside 9front's Ghostscript `icclib`, not kernel/VFS code.

## APIs And Objects

The chunk implements the front half of the icclib C object model declared in `icc.h`.

- File adapters: `new_icmFileStd_fp`, `new_icmFileStd_name`, and `new_icmFileMem` construct `icmFile` implementations backed by `FILE *` or a fixed memory buffer.
- Allocator adapter: `new_icmAllocStd` constructs an `icmAlloc` wrapper around `malloc`, `calloc`, `realloc`, and `free`.
- Primitive codecs: static helpers read/write ICC big-endian integers, fixed-point values, PCS XYZ/Lab encodings, device coordinates, `icmXYZNumber`, and `icmDateTimeNumber`.
- Public string helpers: `tag2str`, `str2tag`, and `icm2str` convert ICC signatures, flags, and enums into readable strings.
- Tag object families: standard `get_size/read/write/dump/allocate/del/new_...` methods are implemented for arrays, curves, data, text, date/time, LUTs, measurement, named color, text description, profile sequence, signature, screening, UCR/BG, VideoCardGamma, viewing conditions, CRD info, and the ICC header.
- Dispatch tables: `typetable[]`, `sigtypetable[]`, and `tagchecktable[]` drive tag construction, legal tag/type matching, and required-tag validation.

## Control Flow

Most tag I/O follows a fixed pattern: validate length, allocate a whole-tag buffer through `icp->al`, seek/read or encode/write through `icp->fp`, validate signatures and internal lengths, allocate variable payload storage, then return `0`, format error `1`, or system/allocation error `2`.

Curve lookup supports linear, gamma, and sampled curves. Reverse sampled lookup lazily builds `icmRevTable` acceleration buckets and falls back to nearest-value matching when no exact reverse interpolation segment is found.

LUT support handles both `icSigLut8Type` and `icSigLut16Type`, applies optional 3x3 matrix, input tables, CLUT interpolation, and output tables, and can build tables from callback functions via `icmLut_set_tables`. CLUT lookup supports n-linear and simplex interpolation.

Top-level `icc_read` stores the file/base offset, reads the 128-byte header and tag table, records each tag's signature/offset/size/type, and leaves payload objects unread for lazy loading by later code.

## State And Dependencies

State is heap-owned through the parent `icc` allocator. Variable objects track allocated sizes separately from logical sizes (`_size`, `_count`, `_channels`, `inputTable_size`, `clutTable_size`, `outputTable_size`) to support resizing.

Dependencies include standard C/POSIX headers, `icc.h`/`icc9809.h`, math functions (`pow`, `floor`, `ceil`, `fabs`), ICC constants/signatures, and color helpers referenced but defined later such as `icmXYZ2Lab`, `icmD50`, and `getNormFunc`.

## Risks And Edge Cases

Size calculations often multiply untrusted profile values in `unsigned int`/`unsigned long`, especially LUT table sizes and tag table allocation, so malformed large profiles may overflow before allocation or bounds checks.

The memory-file adapter uses `(cur + len) >= end`, which truncates exact-end reads/writes and performs pointer arithmetic before full bounds validation. Static string buffers in conversion helpers are not thread-safe.

Some error paths leak buffers or have surprising ownership behavior, notably `icmVideoCardGamma_read` returning without freeing `buf` in several branches and calling `pp->del(pp)` for unsupported table entry sizes. Dump/error routines also contain minor bugs and typo-quality diagnostics.

`#undef ICM_STRICT` intentionally accepts some non-conforming profile text-description layouts, improving compatibility while reducing strict validation.

## Cross-Chunk References

This chunk forward-declares `getNormFunc` and references color conversion helpers implemented after line 9299. The later chunk must cover normalization functions, color transforms, lookup-object construction, reverse LUT logic, top-level `icc_get_size/write/find_tag/read_tag/add_tag/delete/dump/delete`, and `new_icc`/`new_icc_a`.

`DO_ALIGN` and the `icc_get_size` body begin at the chunk boundary, so final profile layout/write behavior is unresolved here.

### Chunk 2: lines 9300-12776

# Chunk Research: sources/os/plan9/9front/sys/src/cmd/gs/icclib/icc.c lines 9300-12776

## Scope

This chunk covers the end of `icc.c`: ICC profile sizing/writing, tag table mutation/loading/lifetime helpers, lookup normalization tables, color math utilities, monochrome/matrix/LUT lookup-object implementations, lookup-object dispatch by profile class, and public `icc` object construction. It follows prior-chunk definitions for `icc`, `icmBase`, tag/type tables, primitive serializers, tag implementations, `icmLut` interpolation, and legality checking.

## APIs and Entry Points

- `icc_get_size()` computes serialized profile length after `check_icc_legal()`, adding the 128-byte header, aligned tag table, and each unique tag object once by using `icmBase.touched` to avoid double-counting linked tags.
- `icc_write()` serializes a complete profile to an `icmFile` at a caller-supplied offset. It sets `p->fp`/`p->of`, computes aligned offsets and sizes, writes the header, writes the 4-byte count plus 12-byte tag records, then writes each unique tag object once and flushes.
- Tag management methods exported through the `icc` vtable:
  - `icc_add_tag()` validates signature/type compatibility through `sigtypetable`, validates implementation support through `typetable`, prevents duplicate signatures, grows `p->data`, allocates a new type object, and appends an `icmTag`.
  - `icc_link_tag()` appends a new signature that shares an existing loaded tag object, preserving type/offset/size and incrementing the shared object's `refcount`.
  - `icc_find_tag()` reports found/unsupported/missing without setting `p->errc`.
  - `icc_read_tag()` lazily materializes a tag, links to an already-loaded tag with identical type/offset/size, or constructs and reads through `typetable[j].new_obj()`.
  - `icc_rename_tag()` changes an existing tag signature after validating that the new signature can legally carry the current tag type.
  - `icc_unread_tag()` drops a loaded tag object reference and deletes the object when its `refcount` reaches zero.
  - `icc_delete_tag()` drops any object reference, shifts the tag array down, and decrements `p->count`.
  - `icc_read_all_tags()` forces every tag to be loaded.
  - `icc_dump()` prints the header and each tag, temporarily loading unloaded tags for dump output.
  - `icc_delete()` frees the header, tag objects by reference count, tag table, profile object, and optional allocator.
- Lookup/color utility exports visible in this chunk:
  - `icmXYZ2Lab()`, `icmLab2XYZ()`, `icmLabDE()`, `icmLabDEsq()`, `icmCIE94()`, `icmCIE94sq()`, and `icmChromAdaptMatrix()`.
  - Global illuminants/points: `icmD50`, `icmD65`, `icmBlack`.
- Lookup-object factory:
  - `icc_get_luobj()` is assigned to `p->get_luobj` and returns an `icmLuBase *` implementation for requested `icmLookupFunc`, rendering intent, PCS override, and representation search order.
- Constructors:
  - `new_icc_a(icmAlloc *al)` creates an `icc` object, creates/owns a default allocator when `al == NULL`, installs all method pointers, creates a header, and initializes required fields to sentinel values and default fields to Argyll/D50/version/platform defaults.
  - `new_icc()` is a backwards-compatible wrapper over `new_icc_a(NULL)`.

## Control Flow

### Profile Serialization

`icc_get_size()` and `icc_write()` both rely on prior legality validation and the same alignment scheme. `icc_write()` computes offsets in two passes: first it zeroes every loaded object's `touched`, then it walks `p->data`. The first occurrence of a shared object gets a fresh aligned offset and size; subsequent linked tags find the first matching object pointer and copy its offset/size. It writes the tag table before tag payloads. After a payload is written, `touched` is reset to zero so linked later entries are skipped.

Important error exits mostly set `p->err`/`p->errc`, but one linked-tag corruption path in `icc_write()` returns without freeing the tag-table buffer.

### Tag Object Lifetime

Loaded tag payload objects are shared by raw pointer and protected only by `icmBase.refcount`. Links are created explicitly by `icc_link_tag()` or implicitly by `icc_read_tag()` when two tag table entries have equal `ttype`, `offset`, and `size` and one is already loaded. Unreading/deleting/deleting-profile decrements `refcount` and calls the tag object's `del()` when it reaches zero.

`icc_dump()` has special temporary-load behavior: if a tag was not loaded, it reads it, dumps it, decrements `refcount`, deletes the object, and clears `objp`.

### Normalization and Range Selection

The LUT code treats in-memory LUT values as normalized `0.0..1.0` and maps PCS/device spaces through function tables:

- `colnormtable[]` maps color-space signatures to `fromLut8`, `fromLut16`, `toLut8`, and `toLut16` conversion functions.
- `getNormFunc()` selects one conversion function for a color space, LUT tag type (`icSigLut8Type` or `icSigLut16Type`), and direction flag (`icmFromLuti`, `icmFromLutv`, `icmToLuti`, `icmToLutv`).
- `colorrangetable[]` plus `getRange()` provides typical min/max ranges used by monochrome/matrix lookup objects.

Unsupported spaces return failure rather than populating `icc` error state from `getNormFunc()` itself; callers in `new_icmLuLut()` translate that into `icc_get_luobj: Unknown colorspace`.

### Color Math

The chunk includes local 3x3 determinant/adjoint/inverse helpers, `icmMulBy3x3()`, Lab/XYZ conversion using the profile white point, simple Delta E and CIE94 color-difference functions, and Bradford/Von Kries chromatic adaptation. `icmChromAdaptMatrix()` optionally starts from identity or multiplies into an existing matrix, transforms white points into Bradford cone space when requested, applies diagonal white-point scaling, then transforms back.

### Monochrome Lookup

`new_icmLuMono()` creates an `icmLuMono` object if the profile has one device channel and PCS is XYZ or Lab, then requires `icSigGrayTRCTag` as an `icSigCurveType`. It installs public and component function pointers and stores profile/native/effective spaces, intent, white/black points, PCS illuminant, and absolute/relative adaptation matrices.

Forward lookup:

1. `icmLuMonoFwd_curve()` maps device gray through `grayCurve->lookup_fwd()`.
2. `icmLuMonoFwd_map()` scales PCS white by the linearized gray value, converting PCS white to Lab first when native PCS is Lab.
3. `icmLuMonoFwd_abs()` applies absolute colorimetric adaptation when requested, otherwise converts native PCS to effective PCS if Lab/XYZ override differs.

Backward lookup:

1. `icmLuMonoBwd_abs()` forces input PCS to a monochrome locus, then converts absolute/effective PCS back to native PCS.
2. `icmLuMonoBwd_map()` reduces PCS luminance to a single linearized gray value.
3. `icmLuMonoBwd_curve()` maps through `grayCurve->lookup_bwd()`.

Note: `new_icmLuMono()` assigns the component pointers `bwd_abs`, `bwd_map`, and `bwd_curve` to forward component functions even though `bwd_lookup` uses the correct backward static functions directly. Code that calls the component function pointers individually would get forward behavior for the backward components.

### Matrix Lookup

`new_icmLuMatrix()` requires RGB-style TRC tags (`RedTRC`, `GreenTRC`, `BlueTRC`) and XYZ colorant tags (`RedColorant`, `GreenColorant`, `BlueColorant`) with at least one XYZ value each. It builds a 3x3 colorant matrix from X/Y/Z rows and red/green/blue columns, computes its inverse, stores spaces/intents/points, and creates absolute adaptation matrices.

Forward lookup applies red/green/blue forward curves, multiplies by the colorant matrix, applies absolute conversion if requested, and converts XYZ to Lab if effective PCS is Lab. Backward lookup converts effective Lab to XYZ if needed, applies absolute-to-relative adaptation if requested, multiplies by the inverse matrix, and applies backward TRCs.

Risk: `icmLuMatrixBwd_curve()` ignores its `in` argument and calls `lookup_bwd()` using `&out[n]` for both input and output. It works for the current caller because `icmLuMatrixBwd_lookup()` passes `out` in-place after matrix multiplication, but the component API signature suggests it should accept a separate input vector.

### LUT Lookup

`new_icmLuLut()` builds an `icmLuLut` around an `icmLut` tag (`AToB*`, `BToA*`, `Gamut`, or `Preview*`). It requires the tag's type to be `icSigLut8Type` or `icSigLut16Type`, chooses whether to use the LUT matrix when native input is XYZ and `lut->nu_matrix()` reports non-unity, installs native/effective normalization functions, and selects CLUT interpolation.

Forward `icmLuLut_lookup()` performs:

1. `in_abs`: effective-to-native input conversion and absolute-to-relative handling for backward/gamut/preview absolute requests.
2. optional LUT matrix multiplication.
3. native input normalization.
4. input table lookup.
5. CLUT interpolation via selected `lookup_clut`.
6. output table lookup.
7. output denormalization.
8. `out_abs`: native-to-effective output conversion and relative-to-absolute handling for forward/preview absolute requests.

Component functions (`in_abs`, `matrix`, `input`, `clut`, `output`, `out_abs`) expose the same stages individually. Inverse helper stages also exist for output table, input table, matrix, and absolute conversion, using lazily initialized reverse interpolation tables `lut->rot` and `lut->rit`; full inverse CLUT is explicitly absent.

The CLUT interpolation selector prefers simplex for device-like input spaces where luminance varies along the diagonal (`RGB`, `Gray`, `CMYK`, `CMY`, `Mch6`), N-linear for spaces with a single luminance-like channel (`Lab`, `Luv`, `YCbCr`, `Yxy`, `XYZ`, `Hls`, `Hsv`), and otherwise tries to infer diagonal dominance from `lut->min_max()` before falling back to N-linear.

Risk: several copy loops in LUT absolute-conversion helpers use `lut->inputChan` even when copying output-side vectors, which is harmless only when dimensions match or the extra slots are unused.

### Lookup Dispatch

`icc_get_luobj()` starts by running `check_icc_legal()`, determining native/effective PCS from the header and optional override, and loading media white/black point tags. Missing media white is fatal only for absolute colorimetric requests; otherwise D50 is used. Missing media black defaults to zero.

Dispatch by `header->deviceClass`:

- Input/display profiles accept only default or absolute intent and support device-to-PCS (`icmFwd`) and PCS-to-device (`icmBwd`). Default order tries LUT, matrix, then mono; reverse order tries mono, matrix, then LUT.
- Output profiles support forward/backward per intent (`Perceptual` -> `AToB0`/`BToA0`, relative/absolute -> `AToB1`/`BToA1`, saturation -> `AToB2`/`BToA2`), gamut (`icSigGamutTag` PCS-to-gray, default intent only), and preview (`Preview0/1/2` PCS-to-PCS, no absolute).
- Link profiles require default or header rendering intent and use `AToB0`/`BToA0` for device-to-device transforms.
- Abstract profiles require default intent and use `AToB0`/`BToA0` for PCS-to-PCS transforms.
- ColorSpace profiles require default intent and use `AToB0`/`BToA0` for device/PCS transforms.
- NamedColor profiles are recognized but lookup is not implemented.

If a candidate factory fails, `icc_get_luobj()` often keeps trying alternatives. This means error text from failed candidates may remain in `p->err` even when a later candidate succeeds, unless callers ignore stale error state on non-NULL return.

## State and Dependencies

- Shared `icc` state used here: `p->header`, `p->data`, `p->count`, `p->fp`, `p->of`, `p->al`, `p->del_al`, `p->err`, and `p->errc`.
- Shared tag state: `icmTag.sig`, `ttype`, `offset`, `size`, `objp`; `icmBase.refcount`, `touched`, `get_size`, `read`, `write`, `dump`, and `del`.
- Tables defined in earlier chunks and consumed here: `sigtypetable`, `typetable`, and ICC tag/type signatures.
- Serializer/file dependencies from earlier chunks: `write_UInt32Number()`, `write_SInt32Number()`, `icmFile.seek/write/flush`, and `icmHeader` methods.
- LUT dependencies from earlier chunks: `icmLut.lookup_matrix`, `lookup_input`, `lookup_output`, `lookup_clut_nl`, `lookup_clut_sx`, `min_max`, `nu_matrix`, `inputChan`, `outputChan`, `inputEnt`, `outputEnt`, `inputTable`, `outputTable`, matrix `e`, reverse-table caches `rit`/`rot`, and `icmTable_setup_bwd()` / `icmTable_lookup_bwd()`.
- Color-space metadata: `number_ColorSpaceSignature()` is used for component counts in spaces/range APIs.
- Math/library dependencies: `fabs`, `sqrt`, `pow`; `FILE *` for dumps; allocator callbacks for all object allocation.

## Risks and Edge Cases

- `sprintf()` writes into fixed profile error buffers throughout this chunk; safety depends on the buffer size defined elsewhere.
- Profile/tag size and offset arithmetic uses `unsigned int`, so very large profiles may overflow size accounting.
- `icc_write()` frees `buf` after the tag table write, but on tag payload write failure it returns immediately after `buf` has already been freed; that is OK. The later flush failure path calls `free(buf)` again after `buf` was already freed, creating a double-free risk.
- `icc_write()` linked-tag corruption returns without freeing the tag table buffer.
- `icc_delete_tag()` does not shrink/realloc the tag table and leaves stale data beyond `p->count`; normally benign but observable if code misuses count.
- `icc_rename_tag()` does not check whether `sigNew` already exists, so it can create duplicate tag signatures despite add/link preventing duplicates.
- Lazy tag linking in `icc_read_tag()` assumes matching type/offset/size means shared identity; malformed profiles with overlapping or duplicate offsets will share one object.
- Lookup objects borrow tag objects from the parent `icc`; deleting/unreading tags while lookup objects exist can leave dangling pointers.
- Lookup methods OR together return values where `1` means clipping and `2` means error. Once an error path sets `rv` to `2`, later stages may still run unless the component function returns early internally.
- Absolute adaptation divides by source white components without zero checks.
- Named color lookup is intentionally unimplemented.

## Cross-Chunk References

- Begins mid-function: line 9300 is inside `icc_get_size()`, whose declaration and `DO_ALIGN` definition begin just before this chunk at lines 9294-9299.
- Uses `check_icc_legal()` from the previous chunk (starts line 9149) before sizing, writing, and lookup construction.
- Uses `icc_read()` from the previous chunk (starts line 9218), and `new_icc_a()` installs it as the public `read` method.
- Relies on header read/write/dump and `new_icmHeader()` from the previous chunk (around lines 8650-8899).
- Relies on tag implementation constructors in `typetable[]` and signature/type compatibility in `sigtypetable[]`, defined before this chunk around lines 8906-9147.
- Relies on `icmLut` interpolation/table setup code from earlier in the file (notably lines 4140-5301) for LUT lookup object behavior.
- Relies on `icc.h` struct layouts and public vtable fields for `icmLuBase`, `icmLuMono`, `icmLuMatrix`, `icmLuLut`, and `icc`.
