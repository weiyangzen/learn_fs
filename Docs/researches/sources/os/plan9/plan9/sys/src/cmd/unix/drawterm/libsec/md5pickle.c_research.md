# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md5pickle.c

Implements serialization helpers for an in-progress MD5 state: `md5pickle` and `md5unpickle`. It includes `os.h` and `<libsec.h>`.

`md5pickle` allocates a text buffer, prints the four MD5 state words as fixed-width hex fields, then base64-encodes the buffered partial block. `md5unpickle` parses those four words, decodes the base64 buffer into `s->buf`, and marks the returned state as malloced and seeded.

Important limitation: the pickle does not serialize `s->len`; only state words and partial buffer length are reconstructed. That may be sufficient for the original caller convention but is not a full generic MD5 checkpoint.
