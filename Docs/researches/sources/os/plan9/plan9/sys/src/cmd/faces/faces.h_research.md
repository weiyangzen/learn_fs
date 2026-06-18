# File Research: sources/os/plan9/plan9/sys/src/cmd/faces/faces.h

Shared header for the `faces` mail notifier.

Key contents:
- String slots for user, domain, show path, and digest.
- `Facesize` fixed at 48 pixels.
- `Face` structure with image/mask pointers, identity strings, recency/time state, unknown flag, and backing `Facefile`.
- `Facefile` cache structure with image, mask, mtime, read time, refcount, filename, and next pointer.
- Global mail directory state and prototypes across UI, plumbing, database, and utility files.

Important relationships:
- `Face.bit` and `Face.mask` usually alias `Facefile.image` and `Facefile.mask`, except for fallback/error images.
- `maildirs` and `nmaildirs` are owned by `plumb.c` but consumed by `main.c`.
