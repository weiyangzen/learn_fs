# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/readcert.c

Provides certificate-file loading helper `readcert(char *filename, int *pcertlen)`. It includes `<u.h>`, `<libc.h>`, `<mp.h>`, and `<libsec.h>`.

A static `readfile` opens a file, obtains its length with `dirfstat`, allocates a NUL-terminated buffer, reads the full file with `readn`, and returns the string. `readcert` then calls `decodepem(pem, "CERTIFICATE", pcertlen)` and returns the decoded DER bytes.

Errors set `werrstr` for read or parse failure. One edge detail: if `dirfstat` fails, `readfile` returns without closing the already-open fd.
