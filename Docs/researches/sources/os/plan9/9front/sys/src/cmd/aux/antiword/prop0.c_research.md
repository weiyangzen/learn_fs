# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/prop0.c

Word for DOS property extractor for document, section, paragraph, and character formatting metadata.

Key responsibilities:
- Parses DOS-style summary dates and converts them to `time_t`.
- Reads DOP-like document defaults, including default tab width and creation/revision dates.
- Reads section descriptor pages and extracts basic section properties such as new-page behavior.
- Reads paragraph property pages, derives style records, heading levels, alignment, indents, and spacing.
- Reads character property pages, derives font number, size, bold/italic/underline/strike/caps/hidden/subscript/superscript/color state.
- Adds parsed document, section, style, and font records to the shared Antiword info lists.

Dependencies:
- Uses 128-byte Word for DOS block/page structures, endian accessors, file reads, stylesheet defaults, and list insertion helpers.

Notable risks:
- Many offsets and structure lengths are fixed to old Word for DOS layouts.
- Invalid FODO offsets are skipped silently except for debug diagnostics.
- Date parsing accepts flexible separators but only two-digit years.
