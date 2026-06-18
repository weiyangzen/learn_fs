# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdf.c

This file is the main Ghostscript PDF-writing driver. It defines the `pdfwrite` and `ps2write` device prototypes through repeated inclusion of `gdevpdfb.h` with different macros, then implements device open, output-page, close, PDF object initialization, page state reset, encryption setup, color model switching, and final PDF assembly.

The file starts with GC descriptors for `gx_device_pdf`, page arrays, and substream-save structures. It enumerates and relocates device-owned pointers, resource chains, outline action pointers, parameter strings, constant strings, and the base `st_device_psdf` fields.

Temporary-file handling is central. `pdf_open_temp_file` and `pdf_open_temp_stream` create scratch files/streams for xref, asides, streams, and pictures. `pdf_close_temp_file` flushes and frees stream state, closes the file, and unlinks the scratch path. `pdf_close_files` closes all temporary storage paths.

`pdf_initialize_ids` initializes object numbering, creates named Catalog and Info dictionaries, stores default `/Producer`, sets creation/modification dates, and allocates the Pages tree. `pdf_compute_fileID` hashes timing, output filename, and Info dictionary contents to create a document ID. `pdf_compute_encryption_data` implements Standard Security Handler setup for revisions 2 and 3 with MD5 and RC4, validates PDF/X and compatibility constraints, computes owner/user keys, permissions, and encryption key material.

`pdf_set_process_color_model` switches device color info and mapping procedures among DeviceGray, DeviceRGB, DeviceCMYK, and DeviceN-as-CMYK. It updates separable/linear component masks and encode/decode procedures.

`pdf_open` creates temporary storage, opens the vector output file, initializes vector state, named-object dictionaries, IDs, file ID, optional encryption, text data, substream stack, page array, resource chains, outlines, articles, destinations, page labels, and per-page graphics/text state. `pdf_reset_page` restores per-page state, resets graphics, text-page tracking, procsets, patterns, and clipping.

Page lifecycle is handled by `pdf_output_page` and `pdf_close_page`. Closing a page ensures the document is open, closes contents, records media box, contents ID, copy count, resources, text data, dominant rotation, DSC-derived page info, and then resets state. `pdf_write_page` later emits the actual `/Page` object with `/MediaBox`, optional `/TrimBox`, `/Rotate`, `/Parent`, `/Group`, resources, annotations, contents, and extra pdfmark-inserted dictionary entries.

`pdf_close` completes the document: it ensures at least one page exists, writes all page objects, writes/free resource objects, builds the `/Pages` tree, closes outlines/articles/destinations/page labels, writes the Catalog, writes named objects, copies aside resources into the main stream, writes the encryption dictionary if needed, emits the xref table and trailer with `/ID`, frees resource records and named objects, closes vector filters, warns on pdfmark destinations beyond the last page, and closes temporary files.
