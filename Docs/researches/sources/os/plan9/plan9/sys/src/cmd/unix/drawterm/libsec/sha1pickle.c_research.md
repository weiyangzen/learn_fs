# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/sha1pickle.c

Implements serialization helpers for in-progress SHA1 state: `sha1pickle` and `sha1unpickle`. It includes `os.h` and `<libsec.h>`.

`sha1pickle` allocates text, prints the five SHA1 state words as fixed-width hex fields, then base64-encodes the buffered partial block. `sha1unpickle` parses the five state words, decodes the base64 partial buffer, and marks the returned state as malloced and seeded.

As with `md5pickle.c`, the serialized form does not include the total byte count `len`, so it is not a complete generic checkpoint unless surrounding protocol state supplies the missing length.
