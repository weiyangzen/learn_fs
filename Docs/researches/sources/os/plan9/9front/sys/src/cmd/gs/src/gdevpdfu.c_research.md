# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfu.c

Core output utility implementation for the Ghostscript `pdfwrite` driver. It owns document opening, object IDs and xref positions, content-stream context transitions, encryption, resource lifecycle, page helpers, PDF value writing, filter dictionary writing, generic data streams, function resources, and font bounding boxes.

Key behavior:
- Copies and strips OPDF-read procsets, with optional filtering/compression and TrueType-related skipping.
- Opens the PDF document header, writes binary marker bytes when allowed, and selects page compression mode.
- Allocates object IDs, records xref positions, opens/closes numbered objects, and handles separate/asides streams.
- Manages page content contexts through state transitions among none, stream, text, and string contexts.
- Starts page content streams with scaling from device resolution to default user space, optional rendering intent, encryption, and Flate/LZW compression.
- Closes page content streams, writes stream lengths, restores viewer state, and closes compression/encryption filters.
- Implements PDF object encryption key derivation and ARC4 stream/string encryption helpers.
- Maintains resource chains by type, including allocation, cancellation, forgetting, substitution/deduplication, lookup by Ghostscript ID/resource ID, dropping by condition, statistics, writing, reversing, and freeing.
- Stores per-page resource dictionaries and ProcSet usage.
- Copies temporary stream data safely, including same-file copy handling and optional encryption during final copy.
- Grows the page table on demand and allocates page dictionaries and IDs.
- Opens current pages and unclipped stream contexts.
- Writes matrices, PDF names with escaping, strings, arrays/dictionaries with encrypted string elements, and generic serialized values.
- Writes filter and decode-parameter dictionaries for ASCII85, CCITT, DCT, Flate, LZW, PNG predictor, and RunLength filters.
- Begins and ends generic data streams and writes function resources from Ghostscript function objects.
- Supports sampled/function data streams, function arrays, scaled functions, and function resource substitution.
- Writes font bounding boxes, expanding empty boxes to avoid Acrobat display issues.

Notable dependencies:
- Ghostscript stream filters: ASCII85, CCITT, DCT, LZW, PNG predictor, RunLength, ARC4, MD5, zlib.
- COS object APIs from `gdevpdfo.h`.
- PDF graphics/color/font helpers from `gdevpdfg.h`, `gdevpdfx.h`, and `gdevpdtd.h`.

Research notes:
- The file is the central low-level backend for many other `gdevpdf*` modules.
- Temporary streams are deliberately not encrypted while being accumulated because they may be compared for deduplication; encryption is applied when copying to final output.
- Resource deduplication uses COS object equality plus optional type-specific equality callbacks.
- The compatibility comments retain older PDF 1.2/LZW paths, though current comments say Flate is always available for supported levels.
- This is PDF file generation infrastructure, not filesystem code.
