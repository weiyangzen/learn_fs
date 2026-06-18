# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_dir.h

This header defines FAT/PCFS directory-entry formats, filename rules, long-filename handling, and directory search result structures.

Short directory entries:
- `PCFNAMESIZE` is 8, `PCFEXTSIZE` is 3, max long name is 255, and long-name chunk size is 13 UTF-16 characters.
- `struct pctime` stores DOS time/date fields.
- Time/date bit shifts and masks decode seconds, minutes, hours, day, month, and year.
- `struct pcdir` is the traditional FAT 8.3 entry with filename, extension, attributes, NT attrs, creation/last access/modify times, starting cluster low/high fields, and file size.

Long filename entries:
- `struct pcdir_lfn` overlays FAT directory entries for VFAT long names.
- It contains ordinal, three UTF-16 name fragments, LFN attribute/type/checksum, and unused cluster field.
- LFN detection requires enabled long filenames, R/H/S/V attributes only, and valid ordinal 1..20.
- The header documents reverse ordering, checksum association with the short name, case-insensitive long-name lookup, and `0xff` padding behavior.

Attributes and name tests:
- FAT attributes include readonly, hidden, system, label, directory, and archive.
- `PCA_IS_HIDDEN` hides labels and hidden/system files unless the mount flag shows them.
- Macros detect dot/dotdot in long and short forms.
- `pc_invalchar` and `pc_validchar` enforce uppercase ASCII 8.3 character restrictions.

Directory search:
- `pcslot` records lookup result status, disk block, offset, buffer, entry pointer, and dot/dotdot flags.
- `pc_dirent` mirrors `dirent64` layout with a 512-byte name buffer for 256 UTF-16 bytes.

Kernel API:
- Time conversion, LFN validation, read/match/extract long/short names, checksum, chunk setting, name conversion, and starting-cluster get/set helpers.
- Private tunable `enable_long_filenames` controls VFAT LFN recognition.

Dependencies and relationships:
- Includes `pc_node.h` after initial structure declarations because directory code depends on PCFS node types and attributes.
- Works with `pc_fs.h` mount state and FAT cluster logic.
