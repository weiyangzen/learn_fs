# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrd.c

## Role

`gscrd.c` creates and initializes Ghostscript CIE Color Rendering Dictionaries (CRDs), defines default CRD procedures, cache-backed procedure wrappers, and TransformPQR procedure lookup through device parameters.

This is color-management infrastructure, not filesystem code.

## Main Public Interfaces

- `TransformPQR_default`
- `TransformPQR_from_cache`
- `TransformPQR_lookup_proc_name`
- `Encode_default`
- `EncodeLMN_from_cache`
- `EncodeABC_from_cache`
- `RenderTableT_default`
- `RenderTableT_from_cache`
- `gs_cie_render1_build`
- `gs_cie_render1_init_from`
- `gs_cie_render1_initialize`

## Core Behavior

`gs_cie_render1_build` allocates a reference-counted CRD, assigns an ID, initializes GC-visible pointers, marks status built, and returns it.

`gs_cie_render1_init_from` copies all CRD parameters into a CRD, applying defaults for optional values. If `pfrom_crd` is supplied and procedure fields indicate cache-backed procedures, it copies cached EncodeLMN, EncodeABC, or RenderTable.T cache data from the source CRD.

`gs_cie_render1_initialize` is a convenience wrapper with no source-CRD cache copy.

Default procedures are identity transforms. Cache-backed procedures call `gs_cie_cached_value` against existing CRD caches.

TransformPQR procedure-name lookup searches the Ghostscript library device list for the named driver, copies the prototype device, requests the named parameter, reads a procedure pointer from a string parameter, and then calls the resolved procedure.

## GC Support

Defines `st_cie_render1` with GC enumeration/relocation for `client_data`, render-table string table, and TransformPQR procedure data when a render table exists.

## Notable Risks

- TransformPQR device-parameter lookup deserializes a function pointer from string data; this is tightly coupled to trusted in-process device parameters.
- `TransformPQR.proc_data` relocation is conditioned on `RenderTable.lookup.table`, which looks suspicious because TransformPQR data can conceptually exist without a render table.
- The CRD build API has the same reference-count convention noted elsewhere: callers may need to decrement after setting it in graphics state.
