# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfo.c

## Purpose

`gdevpdfo.c` implements Ghostscript pdfwrite's internal COS object model: generic objects, arrays, dictionaries, streams, scalar/constant/object/resource values, serialization, equality checks, stream-piece storage, and a parameter-list writer that serializes Ghostscript parameters into COS dictionaries.

This is support code for PDF generation, not filesystem code.

## Main Object Model

- `cos_object_t` is the common base for all COS objects.
- Concrete types are selected by procedure tables:
  - `cos_generic_procs`
  - `cos_array_procs`
  - `cos_dict_procs`
  - `cos_stream_procs`
- `cos_value_t` stores:
  - scalar copied string values,
  - constant shared string values,
  - object references written as indirect `n 0 R`,
  - resource references written as `/R<n>`.
- Arrays use linked `cos_array_element_t` nodes sorted in decreasing index order.
- Dictionaries and stream dictionaries use linked `cos_dict_element_t` nodes.
- Streams use dictionary elements plus linked `cos_stream_piece_t` nodes that point into the PDF writer's temporary stream file.

## Key APIs

- Object lifetime and writing:
  - `cos_object_alloc`
  - `cos_become`
  - `cos_release`
  - `cos_free`
  - `cos_write`
  - `cos_write_object`
- Value helpers:
  - `cos_string_value`
  - `cos_c_string_value`
  - `cos_object_value`
  - `cos_resource_value`
  - `cos_value_free`
  - `cos_value_write`
- Array helpers:
  - `cos_array_alloc`
  - `cos_array_from_floats`
  - `cos_array_put`
  - `cos_array_put_no_copy`
  - `cos_array_add`
  - `cos_array_add_no_copy`
  - `cos_array_add_c_string`
  - `cos_array_add_int`
  - `cos_array_add_real`
  - `cos_array_add_object`
  - `cos_array_unadd`
  - `cos_array_element_first`
  - `cos_array_element_next`
- Dictionary helpers:
  - `cos_dict_alloc`
  - `cos_dict_put`
  - `cos_dict_put_no_copy`
  - `cos_dict_put_c_key*`
  - `cos_dict_put_string*`
  - `cos_dict_put_c_strings`
  - `cos_dict_move_all`
  - `cos_dict_find`
  - `cos_dict_find_c_key`
  - `cos_dict_elements_write`
  - `cos_dict_objects_write`
  - `cos_dict_objects_delete`
- Stream helpers:
  - `cos_stream_alloc`
  - `cos_stream_dict`
  - `cos_stream_length`
  - `cos_stream_add`
  - `cos_stream_add_bytes`
  - `cos_stream_add_stream_contents`
  - `cos_stream_release_pieces`
  - `cos_stream_elements_write`
  - `cos_stream_contents_write`
  - `cos_write_stream_alloc`
  - `cos_stream_from_pipeline`
  - `cos_write_stream_from_pipeline`

## Serialization Behavior

- Arrays are temporarily reordered into ascending index order for output, with missing indices emitted as `null`.
- Dictionaries are emitted as `<< key value ... >>`; stream dictionaries add `/Length` and then copy accumulated stream pieces.
- Indirect objects are written through `cos_write_object`, which opens a separate PDF object, serializes it, closes it, and marks it `written`.
- `cos_value_write_spaced` delegates scalar syntax to `pdf_write_value`, so PDF names, strings, arrays, dictionaries, encryption, and escaping remain centralized in `gdevpdfu.c`.

## Stream Storage

- Stream data is not kept in memory. `cos_stream_add` records byte ranges already written into `pdev->streams.strm`.
- `cos_stream_contents_write` copies those ranges to output, optionally applying object-specific encryption through ARC4.
- When writing from the same temporary file as the target, it uses `pdf_copy_data_safe`.
- `cos_write_stream_alloc` creates a write stream that forwards bytes into the PDF writer stream file and records the written byte ranges on close/filter flush.

## Parameter Writer

- `cos_param_list_writer_init` creates a `gs_param_list` implementation that writes typed parameters into a COS dictionary.
- `cos_param_put_typed` supports scalar printed parameter serialization plus int and float arrays. String/name arrays are explicitly not implemented and return `typecheck`.

## GC and Memory Ownership

- The file defines Ghostscript GC descriptors and enum/reloc procedures for COS objects, values, array elements, dict elements, and stream pieces.
- Scalar values and owned dictionary keys are heap-owned by the containing collection.
- Constant strings are not copied or freed.
- Non-ID object values are assumed singly referenced and may be freed through their containing value.
- Objects with IDs are manually managed, not reference counted.

## Risks and Edge Cases

- COS objects are not reference counted, so ownership discipline is central.
- Equality for streams assumes identical segmentation of stream pieces; comments state this is not generally true.
- `cos_dict_objects_delete` clears object IDs so later dictionary freeing also frees those objects; this is specialized and hazardous outside its intended close path.
- Several helper buffers are marked ad hoc.
- `cos_param_put_typed` has incomplete support for string/name arrays.
- Error paths can leave allocated objects attached to larger writer state for later cleanup.
