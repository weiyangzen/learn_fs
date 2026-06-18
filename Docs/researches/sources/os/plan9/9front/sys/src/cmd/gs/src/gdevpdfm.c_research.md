# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfm.c

Ghostscript `pdfwrite` pdfmark processor. It receives `pdfmark` pseudo-parameters from PostScript execution, normalizes arguments, resolves named-object references, transforms coordinates, and dispatches each pdfmark type to PDF object/resource construction logic.

Key behavior:
- Provides public utilities for pdfmark handling: `pdf_key_eq`, integer scanning, page reference resolution, destination construction, destination name coercion, rectangle/border parsing, and dictionary pair insertion.
- Implements annotation/link handling through `pdfmark_annot`, mapping pdfmark keys to PDF annotation keys, transforming `/Rect` and `/Border`, and attaching annotations to the correct page’s `/Annots` array.
- Builds outline trees for `OUT` pdfmarks, tracking depth, parent/prev/next/first/last links, `/Count`, implicit destinations, and delayed writing of prior outline nodes.
- Implements article/thread support with bead objects, page references, bead rectangles, and final article dictionaries.
- Handles named destinations via `DEST`, including simple destination arrays and destination dictionaries with extra metadata.
- Handles PostScript pass-through `PS` pdfmarks, either inlining short code or emitting `/Subtype /PS` XObject resources, with optional Level 1 fallback streams.
- Supports document/page dictionary pdfmarks: `PAGES`, `PAGE`, `DOCINFO`, `DOCVIEW`, and `PAGELABEL`.
- Rewrites `/Producer` values in `DOCINFO` when they reference Distiller, replacing the Distiller segment with Ghostscript’s producer string.
- Implements named object pdfmarks: `BP`, `EP`, `SP`, `OBJ`, `PUT`, `.PUTDICT`, `.PUTINTERVAL`, `.PUTSTREAM`, `APPEND`, `CLOSE`, `NamespacePush`, `NamespacePop`, and `NI`.
- Starts and ends form XObject accumulation for `BP`/`EP`, storing `/BBox`, `/Matrix`, `/Resources`, global object flags for OPDF-read mode, and named-object bindings.
- Creates COS arrays, dictionaries, and streams for `/OBJ`, with stream compression setup for pdfmark-owned stream objects.
- Mutates named COS objects through array put/append, dictionary put, stream writes, interval writes, and close state checks.
- Maintains local namespace stacks for named-object scoping and named-image stack entries for later image handling.
- Includes dispatch entries for marked content and document structure pdfmarks, but these handlers currently return success without implementing output.

Notable dependencies:
- COS object APIs from `gdevpdfo.h`.
- Named-object scanning/replacement from `gdevpdfr.c`.
- PDF object/resource/page utilities from `gdevpdfx.h` and `gdevpdfu.c`.
- Stream compression filters from `szlibx.h` and `slzwx.h`.

Research notes:
- The `pdfmark_process` entry point expects the argument array layout `(key,value)*, CTM, type`; it strips the CTM/type, optionally extracts `/_objdef`, substitutes `{name}` references with indirect references, and dispatches by pdfmark name.
- CTM handling is pdfmark-specific: most pdfmarks are converted into default user space, while `BP` and `SP` request the true CTM.
- Named content and document-structure pdfmarks are explicitly marked “NOT IMPLEMENTED YET”.
- This is PDF metadata/resource/output glue, not filesystem code.
