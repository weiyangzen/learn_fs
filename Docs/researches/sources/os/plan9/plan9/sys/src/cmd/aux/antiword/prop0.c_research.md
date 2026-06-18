# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/prop0.c

## Summary
`prop0.c` parses property information from Word for DOS files. It extracts document dates/default tab width, sections, paragraph styles, character font runs, and simple heading/style metadata.

## Main Responsibilities
- Converts DOS-style summary dates to `time_t`.
- Reads Word for DOS summary blocks and creates document info records.
- Reads section descriptors and section property bytes from 128-byte pages.
- Parses section break behavior.
- Parses paragraph property pages into style records, including heading levels, alignment, indents, and before/after spacing.
- Parses character property pages into font records, including bold/italic/underline/strike/caps/hidden, superscript/subscript, font number, size, and color.

## Key Dependencies
Uses direct `bReadBytes()` reads, Word byte/word helpers, style/font/document list builders, stylesheet defaults, and file-offset/character-position conventions.

## Filesystem Relevance
Reads fixed-layout regions from legacy Word for DOS files. No OS filesystem logic.

## Notes
Parsing is conservative: invalid FODO offsets are skipped, and missing section properties fall back to defaults.
