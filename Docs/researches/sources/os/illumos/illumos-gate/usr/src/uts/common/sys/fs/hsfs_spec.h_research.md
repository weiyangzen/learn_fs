# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/hsfs_spec.h

This header defines original High Sierra filesystem on-disk layout constants and accessor macros.

Integer parsing:
- Provides the same byte-access and MSB/LSB/BOTH integer macros used by ISO parsing.
- SPARC uses bytewise parsing to avoid unaligned accesses.

Volume descriptor:
- High Sierra sector size is 2048 bytes and volume descriptors start at sector 16.
- Max file offset is 4 GiB minus 1.
- Volume descriptor types include boot, standard file structure, coded character file structure, unspecified, and end-of-volume.
- Identifier string is `"CDROM"`.
- Defines lengths for system/volume/set/publisher/preparer/application/copyright/abstract/date fields.
- Accessor macros cover descriptor LBN, type, standard id/version, system/volume ids, size, set size/sequence, block size, path table locations, root dir, metadata strings, dates, and file structure version.

Path table:
- Defines fixed entry size and accessors for extent LBN, XAR length, name length, parent number, and name.
- SPARC uses MSB parsing for extent LBN; other platforms directly dereference.

Directory records:
- Defines root record/fixed directory/user extension sizes and maximum name length.
- Accessors cover directory length, XAR length, extent LBN/size, creation date, flags, reserved/interleave/volume set, name length/name, and UNIX extension mode/uid/gid.
- Flag definitions mirror ISO style: existence, directory, associated, record, protection, unused, last extent, and prohibited combinations.
- Provides date macros and regular-file/directory tests.

Kernel declarations:
- Date parsing routines are declared under `_KERNEL`.

Dependencies and relationships:
- Represents High Sierra pre-ISO format, while `hsfs_isospec.h` represents ISO 9660.
- HSFS mount code chooses among HS, ISO, ISO v2, and Joliet formats using these layout definitions.
