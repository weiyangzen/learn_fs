# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfo.c

Ghostscript `pdfwrite` COS object implementation. It supplies the internal object model for PDF arrays, dictionaries, streams, scalar values, resources, object references, writing, equality checks, and memory management.

Key behavior:
- Defines concrete element structures for arrays, dictionaries, and stream content pieces, plus Ghostscript GC descriptors and relocation/enumeration procedures.
- Initializes generic COS objects and allows unresolved generic objects to “become” arrays, dictionaries, or streams for forward-reference pdfmark workflows.
- Represents COS values as scalar strings, constant strings, indirect object references, or resource-name references.
- Handles value copying/freeing rules, including ownership of scalar strings and recursive freeing of un-IDed object values.
- Writes scalar values through `pdf_write_value`, object values inline or as `N 0 R`, and resource values as `/R#`.
- Implements COS arrays with sparse index support: array elements are stored in decreasing index order, temporarily reversed for writing, and missing indices are emitted as `null`.
- Provides array helpers for adding strings, integers, reals, objects, and stack-style `unadd`.
- Implements COS dictionaries with key/value insertion, replacement, move-all, lookup, writing, and deep-ish equality checks.
- Provides a parameter-list writer that serializes Ghostscript typed parameters into a COS dictionary, including integer and float arrays.
- Implements COS streams as dictionary-plus-content-piece objects. Stream data is accumulated in temporary stream storage, then copied into final PDF streams on write.
- Supports stream equality by comparing dictionaries and temporary-file stream pieces, with a noted assumption that compared streams have matching segmentation.
- Implements stream piece append/release, byte append, stream-content copy, and stream length tracking.
- Provides `cos_write_stream_alloc`, a stream adapter that writes into a COS stream and records piece boundaries when closed or flushed.

Notable dependencies:
- PDF output helpers from `gdevpdfx.h` and `gdevpdfu.c`.
- Ghostscript memory/GC infrastructure and stream filters.
- `pdf_copy_data`, `pdf_copy_data_safe`, and encryption helpers for copying stream content into final output.

Research notes:
- COS objects are not reference counted; the code relies on object IDs and ownership conventions.
- Generic objects are intentionally used for forward references and are later mutated to a concrete type.
- Dictionary keys are unsorted and array entries are sparse, matching the internal needs of pdfmark and resource generation rather than a general-purpose PDF object library.
- This file underpins pdfmark and PDF resource construction; it contains no filesystem behavior.
