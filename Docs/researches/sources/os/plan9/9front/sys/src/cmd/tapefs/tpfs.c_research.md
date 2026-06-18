# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/tpfs.c

`tpfs.c` is a read-only `tapefs` backend for old `tp` tape archives.

Format:
- Directory array contains 496 entries plus 8 leading reserved entries.
- Entry fields include 32-byte name, two-byte mode, uid, gid, three-byte size, four-byte modified time, two-byte address, and checksum.
- The code treats DECtape and magtape similarly by scanning all entries and ignoring bad checksums.

Behavior:
- `populate` opens the image, reads the directory, counts bad/good checksums, skips empty/zero-address entries, strips leading `/`, fills `Fileinf`, and inserts entries with `poppath`.
- Prints checksum summary to stderr.
- `doread` seeks to `512 * r->addr + off` and reads into a static buffer.
- Directory population is eager; writes are denied.

Risks:
- Mode uses only `tpp->mode[0] & 0777`, ignoring the second mode byte.
- Static read buffer and minimal validation match the historical/simple backend style.
