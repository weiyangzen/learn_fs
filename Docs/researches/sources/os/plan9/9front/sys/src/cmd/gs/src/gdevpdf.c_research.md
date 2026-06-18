# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdf.c

## Purpose

`gdevpdf.c` is the top-level Ghostscript PDF-writing driver implementation for `pdfwrite` and a related `ps2write` configuration. It owns device open/close, temporary files, object ID initialization, page finalization, PDF page tree/catalog/trailer writing, resource flushing, and standard PDF encryption setup.

## Device Prototypes and GC

The file defines GC descriptors for PDF page arrays, the PDF device, and substream-save arrays. It includes `gdevpdfb.h` twice under different macro definitions to instantiate `gs_pdfwrite_device` and `gs_ps2write_device` with different names, inline-image limits, and OPDF-read behavior.

The device pointer enumeration/relocation code covers inherited psdf device fields, PDF resource chains, outline action pointers, parameter strings, and constant strings.

## Open and Initialization

`pdf_open` creates stable PDF memory, opens temporary files/streams for xref, asides, streams, and pictures, opens the vector output file, initializes vector state, allocates global/local named-object dictionaries and namespace stacks, initializes the Catalog, Info dictionary, and Pages tree, computes a file ID, optionally computes encryption data, allocates text/page/substream state, initializes resource chains and outline state, and resets the current page.

`pdf_initialize_ids` assigns initial object IDs, creates named Catalog and DocInfo dictionaries, sets Producer and creation/modification dates, and creates the Pages dictionary. `pdf_compute_fileID` builds an MD5-based document ID from user time, output filename, and Info dictionary serialization while temporarily disabling encryption.

## Encryption

The file implements standard PDF security handler revisions 2 and 3 using MD5 and RC4 helpers. `pdf_compute_encryption_data` validates PDF/X restrictions, key length, encryption version/revision compatibility, permissions, metadata encryption behavior, and password presence. It computes owner entry `O`, encryption key, and user entry `U` following Adobe's repeated-MD5 and repeated-RC4 loops.

## Color Model Handling

`pdf_set_process_color_model` switches the PDF device among DeviceGray, DeviceRGB, DeviceCMYK, and DeviceN-treated-as-CMYK process models. It updates `color_info`, separable/linear masks, color mapping procs, encode/decode procs, and default color-mapping-proc hooks.

## Page Lifecycle

`pdf_close_page` ensures the document is open, creates an empty stream for OPDF-read empty pages when needed, closes current contents, assigns/records page metadata, stores page resources, writes function resources, optionally closes/free resources early for low viewer-memory settings, closes text page state, accumulates text rotation counts, records DSC page metadata, and resets current page state.

`pdf_write_page` emits a page dictionary: `/MediaBox`, optional `/TrimBox`, optional `/Rotate`, parent Pages reference, optional NumCopies, optional transparency group, resources/procsets, annotations, contents, and pdfmark-added page elements.

`pdf_output_page` closes a page and delegates final output accounting to Ghostscript.

## Closing and Final PDF Assembly

`pdf_close` ensures at least one page exists, closes any current page, writes page objects, resource objects, text document resources, Pages tree, outlines, articles, named destinations, page labels, Catalog, named objects, and accumulated aside resources. It writes the encryption dictionary if needed, then writes the xref table, trailer, `/ID`, optional `/Encrypt`, `startxref`, and EOF marker. It frees resource records, named objects, page arrays, closes OPDF filters, closes vector output, checks destination page references, and removes temp files.

Temporary files are managed by `pdf_open_temp_file`, `pdf_open_temp_stream`, `pdf_close_temp_file`, and `pdf_close_files`.

## Dependencies

The file depends on Ghostscript vector/PDF infrastructure (`gdevpdfx.h`, `gdevpdfg.h`, `gdevpdfo.h`, `gdevpdt.h`), platform file/time helpers, MD5 (`smd5.h`), RC4 (`sarc4.h`), and C runtime file functions.

## Filesystem Relevance

The file uses scratch files, stream buffers, `fseek`, `ftell`, `fread`, `fclose`, and `unlink` to assemble a PDF. These are ordinary output/temp-file operations, not filesystem implementation logic.

## Risks and Notes

The close path is large and order-sensitive: page/resource objects, xref positions, named objects, and temp-file offsets must be emitted in the correct sequence. Encryption validation is strict but old, supporting only revisions 2 and 3. Error handling often preserves the first negative code while continuing cleanup, which is appropriate but easy to regress.
