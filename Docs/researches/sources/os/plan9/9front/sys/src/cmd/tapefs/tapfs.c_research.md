# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/tapfs.c

`tapfs.c` is a read-only `tapefs` backend for old `tap` tape archives.

Format:
- Reads a fixed directory area of 192 entries.
- Each entry includes 32-byte name, one-byte mode, one-byte uid, two-byte size, four-byte timestamp, two-byte tape address, and checksum.
- Starts scanning at `dir[8]`, matching historical layout.

Behavior:
- `populate` opens the image, reads the directory, verifies each entry checksum, skips empty/zero-address entries, strips leading slash, converts metadata to `Fileinf`, and inserts with `poppath`.
- `cvtime` converts old tap timestamps; unless `newtap` is set, it divides by 60 and adds a three-year offset.
- `doread` seeks to `512 * r->addr + off` and reads into a static buffer.
- Directory population is eager; `popdir` is a no-op.
- Writes/truncates/creates are no-ops and `dopermw` denies writes.

Risks:
- Directory entry names are used directly from the on-disk directory buffer.
- Bad checksum entries are reported and skipped, not fatal.
- Static read buffer is not reentrant.
