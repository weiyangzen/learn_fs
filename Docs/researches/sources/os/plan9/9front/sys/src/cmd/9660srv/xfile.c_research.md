# File Research: sources/os/plan9/9front/sys/src/cmd/9660srv/xfile.c

Backing-device and fid lifetime management for `9660srv`.

Key functions:
- `getxdata` opens the requested image/device, validates it is a plain file, deduplicates by qid/type/dev identity, and reference-counts shared backing data.
- `putxdata` decrements backing-device refs, purges cached sectors, closes the fd, and frees the name when no attachments remain.
- `refxfs` manages attached filesystem references and releases backing data/private parser state when the filesystem refcount reaches zero.
- `xfile` manages fid lookup, allocation, cleaning, clunking, hash-bucket move-to-front, and freelist reuse.
- `clean` drops filesystem refs, frees per-fid private state, clears open flags, and resets qid.

Filesystem relevance: direct. It manages 9P fid and mounted-image lifetimes for the ISO filesystem server.
