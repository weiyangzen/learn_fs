# File Research: sources/local-fs/ntfs-3g/ntfsprogs/mkntfs.8.in

Manpage template for `mkntfs(8)`, with `@VERSION@` substituted by the build. It documents `mkntfs` as the NTFS filesystem creation tool and describes usage as `mkntfs [options] device [number-of-sectors]`.

The documented basic options cover quick/fast format, volume label, enabling compression, and no-action dry runs. Advanced options cover cluster size, sector size, partition start sector, heads, sectors per track, MFT zone multiplier, zero-time debug mode, UUID generation, disabling content indexing, and forcing operation on non-block or apparently mounted devices.

Output/help options cover quiet, verbose, debug, version, license, and help modes. The manpage explains valid cluster-size and sector-size ranges, notes that clusters larger than 4096 bytes disable compression, and documents MFT zone multiplier values from 12.5% through 50% of the volume.

Known issues describe possible Windows `chkdsk` warnings about the uppercase file because the generated uppercase table may differ across Windows Unicode versions. The footer lists bug-report contact, authors/porters, availability, and related manpages.

This file is documentation rather than executable code, but it is part of the build/install surface through `Makefile.am` manpage rules and the optional `mkfs.ntfs.8` symlink.
