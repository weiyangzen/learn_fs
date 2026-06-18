# File Research: sources/os/linux/linux/fs/udf/Makefile

## Purpose
Builds the Linux UDF filesystem object/module.

## Main Contents
- Adds `udf.o` when `CONFIG_UDF_FS` is enabled.
- Aggregates UDF implementation objects: allocation, directory, file, inode, partition, superblock, truncation, symlink, metadata helpers, time, and Unicode/name conversion files.

## Cross-File Relationships
- The files in this research group are a subset of the `udf-objs` list.
- Shows module boundaries: UDF is built as one filesystem object from many tightly-coupled C files.

## Risks / Review Notes
- No conditional object selection inside UDF; feature differences are handled inside source code and mount/volume logic.
