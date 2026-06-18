# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/getneeds

This rc script extracts sorted “need” files from a source data file.

Key behaviors:
- Iterates over categories `spec`, `tag`, `aux`, and `status`.
- Greps category-specific lines into a temporary file.
- Sorts by fields, removes duplicate fifth-field values with AWK, then sorts numerically by another field.
- Writes outputs named `needspec`, `needtag`, `needaux`, and `needstatus`.
- Removes temporary `junk*` files per category.

Notable implementation details:
- This is a data-preparation helper, not runtime dictionary logic.
