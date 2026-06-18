# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfu.c

## Purpose

`gdevpdfu.c` is a broad utility layer for Ghostscript's PDF-writing driver. It handles document opening, object IDs and xref position recording, page content state transitions, compression/encryption filters, resource allocation/deduplication, page resource dictionaries, low-level PDF value writing, data-stream setup, Function object creation, procset copying, and miscellaneous helpers.

This is PDF output infrastructure, not filesystem/VFS code.

## Document and Object Lifecycle

- `pdf_open_document` writes optional OPDFRead procsets and the `%PDF-x.y` header, sets binary output behavior, and selects page compression.
- `pdf_stell` reports logical output position, accounting for the asides stream base.
- `pdf_obj_ref` reserves object IDs and records xref positions.
- `pdf_open_obj`, `pdf_begin_obj`, and `pdf_end_obj` emit object wrappers.
- `pdf_open_separate`, `pdf_begin_separate`, and `pdf_end_separate` temporarily switch to the asides stream for resources, annotations, and other non-content objects.

## Page Content Context Management

- `pdf_open_contents` transitions among:
  - `PDF_IN_NONE`
  - `PDF_IN_STREAM`
  - `PDF_IN_TEXT`
  - string/text context.
- Transition helpers open content streams, set page compression/encryption, emit initial coordinate scaling, begin/end text objects, and close streams.
- `pdf_close_contents` closes active content context and emits the final `Q` for the initial page `q`.
- `pdf_open_page` ensures the document and current page dictionary exist before opening requested context.
- `pdf_unclip` restores viewer state out of clipping contexts and returns to unclipped stream context.

## Encryption and Value Writing

- `pdf_object_key` derives per-object ARC4 keys from the document encryption key and object ID.
- `pdf_encrypt_init`, `pdf_begin_encrypt`, and `pdf_end_encrypt` manage encryption filter setup/removal.
- `pdf_put_name_chars`, `pdf_put_name`, `pdf_put_string`, and `pdf_write_value` serialize PDF names, strings, arrays, dictionaries, and scalar values.
- `pdf_put_composite` selectively encrypts string tokens inside serialized arrays/dictionaries.
- `pdf_put_encoded_hex_string` is explicitly unimplemented and returns an error after writing a diagnostic.

## Resource Management

- Resource type names and struct descriptors are declared through `pdf_resource_type_names` and `pdf_resource_type_structs`.
- Allocation/opening:
  - `pdf_alloc_aside`
  - `pdf_begin_aside`
  - `pdf_begin_resource_body`
  - `pdf_begin_resource`
  - `pdf_alloc_resource`
  - `pdf_reserve_object_id`
- Deduplication and cleanup:
  - `pdf_find_resource_by_gs_id`
  - `pdf_find_resource_by_resource_id`
  - `pdf_find_same_resource`
  - `pdf_substitute_resource`
  - `pdf_cancel_resource`
  - `pdf_forget_resource`
  - `pdf_drop_resources`
  - `pdf_write_resource_objects`
  - `pdf_free_resource_objects`
  - `pdf_write_and_free_all_resource_objects`
- Page resource collection:
  - `pdf_store_page_resources` writes per-page resource dictionaries for resources used by the current `used_mask`.

## Stream and Filter Helpers

- `pdf_copy_data` and `pdf_copy_data_safe` copy temporary stream data to output, optionally encrypting.
- `pdf_put_filters` inspects a stream filter pipeline and writes `/Filter` and `/DecodeParms` entries for ASCII85, CCITTFax, DCT, Flate, LZW, PNG predictor, and RunLength filters.
- `pdf_flate_binary` chooses LZW for older compatibility and Flate for newer output.
- `pdf_begin_data`, `pdf_begin_data_stream`, `pdf_append_data_stream_filters`, and `pdf_end_data` set up and finalize data streams, including binary, compression, ASCII85, encryption, and length handling.

## Page Helpers

- `pdf_page_id` grows the page array, creates page dictionaries, and reserves page object IDs.
- `pdf_current_page` returns the current page state.
- `pdf_current_page_dict` ensures and returns the current page dictionary.
- `pdf_write_saved_string` writes and frees saved strings.

## Function Objects

- `pdf_function_scaled` creates a scaled function wrapper when output ranges require it.
- `pdf_function_aux` builds COS dictionary/stream/array representations for Ghostscript functions, including sampled-function data streams and nested function arrays.
- `pdf_function` deduplicates function resources and returns a COS object value.
- `pdf_write_function` writes or resolves a Function object ID.
- `pdf_write_font_bbox` writes `/FontBBox`, expanding empty boxes to avoid Acrobat Reader display problems.

## Procset Support

- `copy_ps_file_stripping`, `copy_procsets`, and `doit` strip comments/whitespace from PostScript procset files and optionally skip TrueType-specific sections.
- `pdf_open_document` uses these when `ForOPDFRead` and `OPDFReadProcsetPath` are enabled.

## Risks and Edge Cases

- Many operations depend on manual stream switching between main/asides/temporary streams.
- `pdf_put_encoded_hex_string` is not implemented.
- Encryption is split: temporary stream data is not encrypted until copied to final output.
- Resource deduplication relies on COS equality; stream equality assumes comparable segmentation in `gdevpdfo.c`.
- Several fixed-size buffers are used for names, filter strings, and function data chunks.
- Resource lifecycle is manual and cross-linked through hash chains and `last_resource`.
- Comments note legacy or compatibility workarounds for Acrobat coordinate limits, Acrobat Reader 4 behavior, and OPDFRead procset compression.
