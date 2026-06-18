# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfo.h

## Purpose

`gdevpdfo.h` declares the internal COS object API used by Ghostscript's pdfwrite driver. It defines the abstract and concrete object structures, value representation, procedure-table type model, ownership assumptions, and public functions implemented in `gdevpdfo.c`.

This header supports PDF generation internals, not filesystem functionality.

## Core Definitions

- Abstract types:
  - `cos_object_t`
  - `cos_stream_t`
  - `cos_dict_t`
  - `cos_array_t`
  - `cos_value_t`
  - `cos_object_procs_t`
  - `cos_type_t`
- Procedure table:
  - `release`
  - `write`
  - `equal`
- `cos_object_struct(...)` macro defines the shared layout for all COS objects:
  - `cos_procs`
  - `id`
  - `elements`
  - `pieces`
  - `pdev`
  - `pres`
  - `is_open`
  - `is_graphics`
  - `written`
  - `length`
  - `input_strm`

## Value Model

`cos_value_t` can hold:

- `COS_VALUE_SCALAR`: heap-allocated string.
- `COS_VALUE_CONST`: shared constant string.
- `COS_VALUE_OBJECT`: object written inline or as indirect reference.
- `COS_VALUE_RESOURCE`: object referenced as a resource name.

The header documents that COS objects are not reference counted. Objects without IDs are assumed to have one owner; objects with IDs are manually managed.

## Declared APIs

The header exposes:

- Object allocation and mutation:
  - `cos_object_alloc`
  - `cos_array_alloc`
  - `cos_array_from_floats`
  - `cos_dict_alloc`
  - `cos_stream_alloc`
  - `cos_become`
- Object writing/lifetime:
  - `cos_release`
  - `cos_write`
  - `cos_write_object`
  - `cos_free`
- Value construction:
  - `cos_string_value`
  - `cos_c_string_value`
  - `cos_object_value`
  - `cos_resource_value`
  - `cos_value_write`
  - `cos_value_free`
- Array mutation/enumeration:
  - `cos_array_put`
  - `cos_array_put_no_copy`
  - `cos_array_add*`
  - `cos_array_unadd`
  - `cos_array_element_first`
  - `cos_array_element_next`
- Dictionary mutation/lookup:
  - `cos_dict_put*`
  - `cos_dict_move_all`
  - `cos_dict_find`
  - `cos_dict_find_c_key`
  - `cos_dict_elements_write`
  - `cos_dict_objects_write`
  - `cos_dict_objects_delete`
- Stream operations:
  - `cos_stream_add`
  - `cos_stream_add_bytes`
  - `cos_stream_add_stream_contents`
  - `cos_stream_release_pieces`
  - `cos_stream_dict`
  - `cos_stream_elements_write`
  - `cos_stream_contents_write`
  - `cos_stream_length`
  - `cos_write_stream_alloc`
  - `cos_stream_from_pipeline`
  - `cos_write_stream_from_pipeline`
- Parameter-list bridge:
  - `cos_param_list_writer_t`
  - `cos_param_list_writer_init`

## Integration Notes

- Depends on Ghostscript `gsparam.h` and the forward-declared `gx_device_pdf`.
- Uses `pdf_resource_t`, `stream`, `gs_memory_t`, `gs_id`, and Ghostscript GC macros/types from surrounding pdfwrite headers.
- The `COS_OBJECT`, `CONST_COS_OBJECT`, `COS_OBJECT_VALUE`, `COS_RESOURCE_VALUE`, `COS_RELEASE`, `COS_WRITE`, `COS_WRITE_OBJECT`, and `COS_FREE` macros are central to how other files cast and manage these objects.

## Risks and Contract Constraints

- The header explicitly warns that COS objects are not reference-counted.
- `_c_` dictionary/string procedures do not copy C-string arguments; callers must ensure lifetime.
- `_no_copy` array/dictionary variants assume strings are already allocated by the same allocator and should be adopted.
- `is_open`, `is_graphics`, and `written` are lightweight state flags used for error checking and writer flow, not comprehensive object lifecycle safety.
