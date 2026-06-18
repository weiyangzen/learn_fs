# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/thumb.c

Implements thumbprint table loading/checking for X.509 SHA1 fingerprints. It includes `<u.h>`, `<libc.h>`, `<bio.h>`, `<auth.h>`, `<mp.h>`, and `<libsec.h>`.

The table has `1<<10` buckets. `okThumbprint` hashes the first two digest bytes to choose a bucket and checks linked-list entries for a matching `SHA1dlen` digest. `freeThumbprints` frees all dynamically allocated list nodes and the table.

Static `loadThumbprints` reads a thumbprint file with `Biobuf`, supports recursive `#include` lines, accepts records beginning with `x509 sha1=...`, decodes hex SHA1 values with `dec16`, and skips entries present in an optional CRL table. `initThumbprints` optionally loads a CRL table first, then loads accepted thumbprints and returns the table.

This file is certificate trust-list support code and is not listed in the `libsec.a` Makefile object list.
