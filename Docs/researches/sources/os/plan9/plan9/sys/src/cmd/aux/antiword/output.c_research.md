# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/output.c

## Summary
`output.c` is Antiword’s generic output dispatcher. It creates/destroys `diagram_type` objects and routes paragraph, substring, page, image, list, table, and prologue/epilogue operations to text, formatted text, PostScript, XML, or PDF backends.

## Main Responsibilities
- Captures current conversion type and encoding from parsed options.
- Initializes the selected backend in `pCreateDiagram()`.
- Finalizes the selected backend in `vDestroyDiagram()`.
- Adds second-stage document metadata/fonts after Word version is known.
- Dispatches line movement, substring output, paragraph starts/ends, page breaks, XML list/table events, and image prologues/epilogues.
- Provides `bAddDummyImage()` and `bAddTableRow()` backend capability shims.

## Key Dependencies
Depends on backend functions in text/FMT/XML/PostScript/PDF modules, global options, and image/table metadata types from `antiword.h`.

## Filesystem Relevance
No direct filesystem interaction beyond writing to `stdout` through backend output functions.

## Notes
This module centralizes output-mode branching, keeping parsing code mostly independent from concrete output formats.
