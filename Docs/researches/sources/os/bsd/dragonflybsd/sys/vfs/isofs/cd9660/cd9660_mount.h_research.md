# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_mount.h

Source read: complete file, 68 lines.

Purpose: Public cd9660 mount argument header.

Key definitions:
- `struct iso_args` carries block device path, export args, owner uid/gid defaults, file and directory masks, mount flags, session start sector, and disk/local charset names for Joliet conversion.
- Flags include disabling Rock Ridge, enabling generation numbers or extended attributes, disabling or relaxing Joliet, enabling kernel iconv, and overriding uid/gid/mode masks.

Integration:
- Copied in by cd9660 mount code in `cd9660_vfsops.c`.
- Charset fields depend on `<sys/iconv.h>` and `ICONV_CSNMAXLEN`.

Risks and review notes:
- Mount behavior is strongly flag-dependent: `ISOFSMNT_NORRIP`, `ISOFSMNT_NOJOLIET`, and `ISOFSMNT_KICONV` alter name parsing and presentation.
