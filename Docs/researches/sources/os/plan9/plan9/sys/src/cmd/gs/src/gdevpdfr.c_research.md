# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfr.c

## Purpose

`gdevpdfr.c` implements named-object support for pdfmark processing. It validates pdfmark object-name syntax, creates and resolves named COS objects, manages local/global namespaces, scans serialized PostScript/PDF-like parameter strings, and replaces `{object}` references with PDF indirect object references.

This is PDF writer support code, not filesystem functionality.

## Main APIs

- `pdf_objname_is_valid(const byte *data, uint size)`: validates `{name}` syntax.
- `pdf_find_named(...)`: looks in local then global named-object dictionaries.
- `pdf_create_named(...)`: creates a named or anonymous generic/COS object, optionally assigning an object ID.
- `pdf_create_named_dict(...)`: convenience creator for dictionaries.
- `pdf_refer_named(...)`: resolves an object or creates a forward reference. It also maps predefined page names such as `{ThisPage}`, `{NextPage}`, `{PrevPage}`, and `{PageN}` to page dictionaries.
- `pdf_make_named(...)`: creates or completes a forward-referenced object of a required type.
- `pdf_make_named_dict(...)`: dictionary variant.
- `pdf_get_named(...)`: resolves a named object and verifies its type.
- `pdf_push_namespace(...)`: pushes current local named-object dictionary and NI stack, then creates fresh local ones.
- `pdf_pop_namespace(...)`: restores the previous local named-object dictionary and NI stack.
- `pdf_scan_token(...)`: scans one token from a parameter string.
- `pdf_scan_token_composite(...)`: scans a composite token such as an array/dictionary as one logical token.
- `pdf_replace_names(...)`: replaces embedded `{name}` references with `n 0 R` strings.

## Named Object Semantics

- Local namespace lookup takes precedence over global lookup.
- Missing non-page names become generic forward-reference objects.
- Page aliases resolve to actual page dictionaries and allocate page IDs as needed.
- `pdf_make_named` rejects attempts to redefine a non-generic object.
- Forward references can be mutated in place from generic to array/dict/stream through `cos_become`.

## Scanner Behavior

- The scanner is PostScript-like, not full PDF syntax.
- Special tokens include `<<`, `>>`, `[`, `]`, `{`, `}`.
- String tokens are skipped with `PSSD` decoding logic.
- Hex strings are scanned to the next `>`.
- It recognizes a Ghostscript extension where names preceded by two null bytes can include non-regular characters until a null terminator.
- Syntax errors are mapped to `gs_error_syntaxerror`, falling back to `rangecheck` when unavailable.

## Name Replacement Flow

- `pdf_replace_names` first scans the full string to compute output size.
- It calls `pdfmark_next_object`, which finds composite `{...}` object references and attempts to resolve them.
- Resolution failures leave the original text unchanged for that reference.
- If replacements are needed, it allocates a new buffer and emits ` <id> 0 R ` around each resolved object ID.

## Risks and Edge Cases

- Scanning is deliberately minimal and not a complete PDF parser.
- Malformed tokens during replacement are skipped by advancing one byte, so bad strings can be partially processed.
- `pdf_replace_names` sets `to->persistent = true`, but ownership of allocated replacement memory depends on later caller cleanup.
- Namespace push/pop assumes the namespace stack remains balanced and ordered as NI stack then local-name dictionary.
- `pdf_pop_namespace` frees current local dictionaries before restoring previous ones; misuse can invalidate active references.
