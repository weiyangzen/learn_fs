# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfo.h

Internal header for `pdfwrite` COS object support. It declares the object/value/container model implemented by `gdevpdfo.c` and exposes the helpers used throughout the PDF-writing driver.

Key contents:
- Defines abstract COS types: `cos_object_t`, `cos_array_t`, `cos_dict_t`, `cos_stream_t`, `cos_value_t`, and associated procedure tables.
- Documents the model: only arrays, dictionaries, and streams are composite COS objects; other PDF syntactic values are stored as printed scalar strings.
- Defines shared object fields through `cos_object_struct`: procedure table, object ID, elements, stream pieces, owning PDF device, resource pointer, open/graphics/written flags, stream length, and optional input stream.
- Defines COS value types: scalar strings, constant strings, indirect object references, and resource-name references.
- Declares allocation functions for generic objects, arrays, dictionaries, streams, and float arrays.
- Declares object lifecycle, type mutation, writing, and value construction APIs.
- Declares array operations for indexed put, append, typed append, stack pop, and enumeration.
- Declares dictionary operations for keyed put, typed put, string put, move-all, and lookup.
- Declares stream operations for adding bytes, adding stream contents, releasing pieces, getting the dictionary, and allocating a stream writer.
- Declares COS stream/dictionary writing helpers and named-object write/delete helpers used at document close.
- Defines `cos_param_list_writer_t`, a Ghostscript parameter-list writer that stores parameters into a COS dictionary.

Research notes:
- The header explicitly states COS objects are not reference counted and that objects without IDs are assumed to be owned by a single parent.
- Procedures containing `_c_` in their names do not copy C string arguments; this ownership convention is important for callers.
- `is_open` and `is_graphics` are mainly pdfmark validation flags for `CLOSE`, `PUT`, and `SP`.
- This is private PDF output infrastructure, not a filesystem-facing API.
