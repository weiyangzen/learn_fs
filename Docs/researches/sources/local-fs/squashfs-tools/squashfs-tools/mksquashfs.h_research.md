# File Research: sources/local-fs/squashfs-tools/squashfs-tools/mksquashfs.h

Central shared interface for mksquashfs build state. It defines directory entries, inode metadata, in-memory file layout, duplicate tracking, fragment metadata, id tables, append mappings, cached directory indexes, exclude/pathname structures, and old-root append metadata.

Important structs: `dir_info`, `dir_ent`, `inode_info`, `file_info`, `dup_info`, `fragment`, `id`, `append_file`, `directory`, `exclude_info`, and path container types. These are the common data model used across scanners, readers, writers, sorters, pseudo files, append mode, and fragment processing.

Defines memory/cache ratios, metadata block offset, inode hash sizing, fragment size, allocation constants, max Linux read size, and `get_pathmax()` capped at 64 KiB.

Declares extensive global pipeline state: caches, queues, fragment table, compressor, block sizing, duplicate/hardlink flags, root options, uid/gid overrides, xattr/pseudo settings, and main build functions such as `create_inode()`, `write_file()`, directory scanning, inode lookup, and `exec_date()`.
