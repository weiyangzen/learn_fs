# File Research: sources/os/plan9/9front/sys/src/9/xen/cppx

`rc`/`awk` wrapper around C preprocessing for Xen headers.

Purpose:
- Preserves selected preprocessor lines while running `cpp -P`.

Key behavior:
- Skips `#include` lines.
- Quotes `#define`, continued macro, `#error`, and `#undef` lines with a temporary quote replacement.
- Pipes through `cpp -P`, then uses `sed` to restore literal quotes and unquote preserved directive text.

Integration:
- Supports generation/import of Xen public header data into Plan 9-compatible forms.

Risks/notes:
- Uses `£` as a temporary quote sentinel, which assumes that character will not occur meaningfully in input.
