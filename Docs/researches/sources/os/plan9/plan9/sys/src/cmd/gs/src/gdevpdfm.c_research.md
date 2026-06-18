# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfm.c

## Purpose

`gdevpdfm.c` implements `pdfmark` processing for Ghostscript's PDF-writing driver. It receives the PostScript-side `pdfmark` pseudo-parameter, normalizes its key/value argument array, resolves named object references, applies CTM transforms where needed, and dispatches to handlers for annotations, links, outlines, articles, destinations, PostScript XObjects, document/catalog/page dictionaries, page labels, named COS objects, and namespace operations.

This is application-level Ghostscript PDF writer code within the Plan 9 source tree, not OS/VFS or filesystem code.

## Main Entry Points

- `pdfmark_process(gx_device_pdf *pdev, const gs_param_string_array *pma)`: central dispatcher. It expects `(... key/value args ..., CTM, mark-type)`, validates the CTM, finds the mark type in `mark_names`, handles `/_objdef`, substitutes named references unless disabled, adjusts CTM unless `PDFMARK_TRUECTM`, then invokes the selected handler.
- `pdf_key_eq(...)`: shared helper for comparing parameter strings to literal keys.
- `pdfmark_scan_int(...)`: parses integer parameter strings.
- `pdfmark_close_outline(...)`: exported outline-level close helper.
- `pdfmark_write_article(...)`: exported article finalization helper.
- `pdfmark_end_pagelabels(...)`: flushes pending page-label state.

## Implemented Pdfmark Families

- Annotation/link marks:
  - `ANN`, `LNK` call `pdfmark_annot`.
  - `pdfmark_put_ao_pairs` performs key remapping such as `/Action` to `/A`, `/Color` to `/C`, `/Title` to `/T`, action subdictionary synthesis, `/Rect` and `/Border` CTM transforms, `/Contents` newline normalization, implicit outline destinations, and special handling for `/GoTo`, `/GoToR`, `/Launch`, and `/Article`.
- Outline marks:
  - `OUT` builds an outline tree incrementally using `pdev->outline_levels`.
  - Nodes are written as separate objects by `pdfmark_write_outline`.
  - Counts and open/closed subtree state are tracked manually.
- Article marks:
  - `ARTICLE` creates or finds article threads by `/Title`, appends beads, transforms bead rectangles, and writes bead/thread objects later.
- Destination and document-view marks:
  - `DEST` writes named destinations into `pdev->Dests`.
  - `DOCVIEW` sets `/OpenAction` or writes catalog pairs.
- PostScript passthrough:
  - `PS` emits inline PostScript for small sources or wraps source/Level1 code as `/Subtype /PS` XObjects.
- Page/document metadata:
  - `PAGES`, `PAGE` write key/value pairs into the pages tree or current page dictionary.
  - `DOCINFO` writes info dictionary entries and rewrites `Producer` strings that contain `Distiller`.
  - `PAGELABEL` accumulates page-label number-tree entries.
- Named object operations:
  - `BP`/`EP` create and close Form XObjects.
  - `SP` paints a named Form XObject.
  - `OBJ`, `PUT`, `.PUTDICT`, `.PUTSTREAM`, `APPEND`, `.PUTINTERVAL`, and `CLOSE` create and mutate named COS arrays/dicts/streams.
  - `NamespacePush`, `NamespacePop`, and `NI` manipulate named-object namespaces and image-reference stacks.
- Marked content and document structure:
  - `MP`, `DP`, `BMC`, `BDC`, `EMC`, `StRoleMap`, `StClassMap`, `StPNE`, `StBookmarkRoot`, `StPush`, `StPop`, `StPopAll`, `StBMC`, `StBDC`, `StOBJ`, `StAttr`, `StStore`, and `StRetrieve` are present as dispatchable stubs returning success without implementation.

## Important State and Dependencies

- Uses COS support from `gdevpdfo.h`, named-object lookup/replacement from `gdevpdfr.c`, and PDF output/resource helpers from `gdevpdfx.h`.
- Updates `gx_device_pdf` state including `next_page`, `max_referred_page`, `Dests`, `Catalog`, `Info`, `Pages`, `PageLabels`, `articles`, `outline_levels`, `outlines_id`, `local_named_objects`, `NI_stack`, `substream_Resources`, and current page annotations.
- Allocates COS dictionaries, arrays, streams, and PDF object IDs through the PDF writer allocator and object-reference helpers.
- Uses stream filters for pdfmark-created streams via `setup_pdfmark_stream_compression`.

## Notable Control Flow

- Destination construction flows through `pdfmark_make_dest`, which combines `/Page` and `/View`, supports `/Next` and `/Prev`, uses page object references for local destinations, and page indexes for remote GoToR actions.
- Named destination strings can be coerced from `(name)` to `/name` by `pdfmark_coerce_dest`, but the code explicitly notes missing escape handling.
- `pdfmark_process` allocates a temporary `pairs` array for every mark, possibly with `/_objdef` removed, then may call `pdf_replace_names` over arguments before dispatch.

## Risks and Edge Cases

- Several comments explicitly mark incomplete behavior, including destination escape handling and PostScript passthrough escape decoding.
- Document-structure and marked-content pdfmarks are accepted but not implemented, which may silently drop accessibility/structure semantics.
- Many parsers use fixed buffers and `sscanf`; malformed or oversized strings return `rangecheck`/`limitcheck`.
- Object/reference ownership is manual. Errors after partial COS allocation often return directly, so callers depend on broader PDF writer lifetime cleanup.
- `/Contents` newline normalization mutates copied dictionary storage in place and resizes it if needed.
- Outline count handling tolerates incorrect/incomplete trees at end-of-document but relies on manual depth/count invariants.
