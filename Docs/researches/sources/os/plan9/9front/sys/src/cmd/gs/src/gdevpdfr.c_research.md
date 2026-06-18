# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfr.c

Named-object and token-scanning support for pdfmark processing. It manages `{name}` object references, local/global named-object namespaces, namespace stack operations, and substitution of named references inside pdfmark argument strings.

Key behavior:
- Validates object-name syntax as `{name}` with braces spanning the full string.
- Looks up named objects first in the current local namespace, then in the global namespace.
- Creates named objects as generic forward references or as typed COS arrays/dictionaries/streams with optional assigned object IDs.
- Resolves predefined page names:
  - `{ThisPage}`
  - `{NextPage}`
  - `{PrevPage}`
  - `{PageN}`
- Maps page names to page dictionary objects by ensuring page IDs exist.
- Supports `pdf_make_named` and `pdf_make_named_dict` for creating or finalizing forward references, rejecting attempts to redefine already typed objects.
- Supports `pdf_get_named` with type checking.
- Pushes and pops local named-object namespaces, also saving/restoring the named-image stack.
- Implements a simplified PostScript-token scanner used for pdfmark strings, including composite array/dictionary token scanning.
- Handles a Ghostscript-specific null-delimited name convention produced by `gs_pdfwr.ps`.
- Replaces `{name}` references in parameter strings with `N 0 R` references through a two-pass sizing/copying process.

Notable dependencies:
- COS dictionary/array/object APIs from `gdevpdfo.h`.
- Page ID allocation from `gdevpdfu.c`.
- Scanner character classes and PostScript string decode helpers.

Research notes:
- The scanner intentionally handles a subset of PostScript syntax, not full PDF syntax.
- Forward references are allowed; unresolved or invalid references are left as literal strings during substitution.
- Namespace push/pop is used by pdfmark scoping and must preserve both named objects and named-image entries.
- This file is pdfmark object-reference plumbing, not filesystem code.
