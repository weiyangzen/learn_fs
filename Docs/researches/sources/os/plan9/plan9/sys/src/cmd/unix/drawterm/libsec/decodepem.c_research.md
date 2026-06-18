# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/decodepem.c

Defines `decodepem(char *s, char *type, int *len)`, extracting and base64-decoding a named PEM section. It includes `<u.h>`, `<libc.h>`, `<mp.h>`, and `<libsec.h>`.

The parser searches line by line for `-----BEGIN <type>-----\n`, then searches for the matching `-----END <type>-----\n`. It tolerates garbage before and after the selected section but expects exact newline-terminated delimiters.

It allocates a decoded buffer sized from the base64 span, calls `dec64`, stores the decoded length through `len`, and returns the allocated DER bytes. On malformed delimiters, allocation failure, or bad base64, it returns `nil` and sets `werrstr`.
