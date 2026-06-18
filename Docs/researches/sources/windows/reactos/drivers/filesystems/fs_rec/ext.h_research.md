# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/ext.h

Packed partial EXT superblock layout used only for recognition. The structure includes the leading ext2/3/4 fields through default reserved UID/GID, including counts, block sizing fields, timestamps, mount counts, magic, state, errors, revision, and creator OS. Compile-time assertions verify representative offsets through `DefResUid` at `0x50`. Constants define the EXT magic `0xEF53`, superblock byte offset `0x400`, and read size `0x400`.
