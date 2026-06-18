# File Research: sources/os/bsd/freebsd-src/sbin/bsdlabel/bsdlabel.c

## Purpose
Reads, displays, edits, restores, writes, and boot-code-installs BSD disk labels. It prints a deprecation warning and directs users toward `gpart`.

## Main Elements
- `main()`: parses `-A`, `-B`, `-b`, `-e`, `-f`, `-m`, `-n`, `-R`, `-r`, `-w`; resolves GEOM device paths; selects operation.
- Operations:
  - `READ`: read and display label.
  - `EDIT`: write label to temp file, invoke editor, parse result, write back.
  - `RESTORE`: parse ASCII protofile and write.
  - `WRITE`: generate label from `auto` or disktab type.
  - `WRITEBOOT`: install boot code while preserving/updating label.
- Label handling:
  - `readlabel()` reads boot area, decodes little-endian disklabel, handles absolute partition offsets.
  - `writelabel()` computes magic/checksum, optionally reads boot code, encodes label into boot area, and writes `bbsize` bytes.
  - `getvirginlabel()` creates an auto label from media size, sector size, and firmware geometry ioctls.
  - `fixlabel()` creates a default `a` partition if no non-raw partitions exist.
- ASCII handling:
  - `display()` emits editable text form.
  - `getasciilabel()` parses label fields and partition lines.
  - `getasciipartspec()` parses partition size, offset, fstype, and FFS/LFS fields.
  - `checklabel()` fills defaults, expands `*`, `%`, and K/M/G/T size suffixes, assigns offsets, checks bounds and overlaps.
- Editor support:
  - `edit()` loops until a valid edit is written or user declines.
  - `editit()` drops effective uid/gid to real ids before invoking `$EDITOR` or `vi`.

## Dependencies And Integration
Uses `libgeom` for provider paths, media geometry, and GEOM class detection; `geom_bsd_enc.c` for label encode/decode; `<sys/disklabel.h>` for structures and constants; `/boot/boot` as default boot code; `/tmp/EdDk.XXXXXXXXXX` for edits.

## Behavioral Notes
Requires `-m i386` or `-m amd64` to set label sector/offset and boot block size. Supports file mode with `-f`, where regular files are treated as disk images.

## Risk Notes
Writes raw boot block areas and partition metadata. `-n` suppresses writes and prints the would-be label. It refuses disks larger than `2^32-1` sectors and caps partitions at 8 due to the local `MAXPARTITIONS` setting.
