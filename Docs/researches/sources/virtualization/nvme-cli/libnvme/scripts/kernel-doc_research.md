# File Research: sources/virtualization/nvme-cli/libnvme/scripts/kernel-doc

This Perl script is a kernel-doc extractor adapted for libnvme documentation generation.

Supported output modes:
- `-man`: troff manual pages.
- `-rst`: reStructuredText, default in this copy.
- `-none`: validation/warnings only.

Supported selection modes:
- All symbols.
- Included `-function NAME` or DOC sections.
- Exported symbols via `EXPORT_SYMBOL`.
- Internal non-exported symbols.
- Exclusions via `-nosymbol`.
- Extra export scan inputs via `-export-file`.

Parser model:
- Scans C comments beginning with `/**`.
- Recognizes function, struct, union, enum, typedef, and `DOC:` blocks.
- Uses state constants for normal code, name, body, prototype, docblock, and inline member docs.
- Parses section names such as Description, Context, Return/Returns, Notes, and Examples.
- Supports inline member documentation inside declarations.
- Parses prototypes, syscall macros, tracepoint macros, structs/unions, enums, typedefs, function pointers, arrays, bitfields, anonymous structs/unions, and common kernel declaration macros.
- Warns about missing/excess parameter documentation and, in verbose mode, missing return documentation.

Output behavior:
- Man output emits `.TH`, `.SH`, `.IP`, and formatted prototypes.
- RST output emits Sphinx C-domain directives, adapting for Sphinx major version before/after 3.
- `-enable-lineno` can emit `#define LINENO` markers in RST mode.
- Highlighting converts kernel-doc syntax for functions, constants, params, structs, enums, typedefs, unions, and members.

Integration role:
- Used by documentation build scripts and `kernel-doc-check`.
- Essential for converting libnvme C API comments into man/RST docs and for CI-style comment validation.
