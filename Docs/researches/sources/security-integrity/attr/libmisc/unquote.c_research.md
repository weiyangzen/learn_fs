## sources/security-integrity/attr/libmisc/unquote.c

Purpose: in-place decoder for backslash-octal sequences.

`unquote` scans for `\NNN` octal escapes and compacts decoded bytes into the input buffer, leaving other backslash sequences mostly unchanged. State is caller-owned mutable string. Dependencies are only libc. Risks include modifying argv or static strings if callers pass non-writable data, accepting partial non-octal escapes literally, and embedded NUL effects after decode. Tests are restore parsing for quoted filenames and names.
