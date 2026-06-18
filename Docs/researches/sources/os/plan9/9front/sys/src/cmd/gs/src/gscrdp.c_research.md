# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrdp.c

## Role

`gscrdp.c` serializes and deserializes device-specified CIE CRDs through Ghostscript parameter lists.

This is device parameter/color-management infrastructure, not filesystem code.

## Main Public Interfaces

- `param_write_cie_render1`
- `param_put_cie_render1`
- `gs_cie_render1_param_initialize`
- `param_get_cie_render1`

## Write Behavior

The writer emits a modified PostScript-style CRD dictionary containing:

- `ColorRenderingType`
- `WhitePoint`
- optional `BlackPoint`
- matrices and ranges when non-default
- sampled `EncodeLMNValues` and `EncodeABCValues`
- optional TransformPQR name/data
- optional render table size/table
- optional sampled `RenderTableTValues`

Sampling is performed from CRD procedures into float arrays sized by `gx_cie_cache_size`.

If TransformPQR is neither default nor name-addressable, writing fails with `rangecheck`.

## Read Behavior

The reader validates `ColorRenderingType`, reads vectors/matrices/ranges, reads optional sampled procedure arrays, reconstructs temporary procedure callbacks backed by stack-local `encode_data_t`, initializes/samples/completes the CRD, then replaces procedure pointers with cache-backed forms where sampled arrays were supplied.

Render tables are validated for dimensions and string sizes, then copied into newly allocated `gs_const_string` arrays referencing parameter-list string data.

## Dependencies

Uses Ghostscript parameter-list APIs, CIE cache/render routines, device names, memory allocation, and render-table interpolation support.

## Notable Risks

- `param_get_cie_render1` temporarily stores `pcrd->client_data = &data` where `data` is stack-local; it resets `client_data` before return, relying on all cache completion happening synchronously.
- Render table string data is referenced from the parameter list data; the allocated table copies string descriptors, not underlying bytes.
- Writer comments mark `pd.persistent = true` for TransformPQRData as “WRONG,” indicating an acknowledged lifetime/ownership issue.
- Error cleanup for partially allocated render-table structures is limited and depends on downstream ownership conventions.
