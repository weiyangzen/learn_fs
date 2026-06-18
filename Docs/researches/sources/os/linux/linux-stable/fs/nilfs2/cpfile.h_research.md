# File Research: sources/os/linux/linux-stable/fs/nilfs2/cpfile.h

## Summary
Declares the NILFS checkpoint-file API used by checkpoint management, mount, ioctl, and root loading code.

## Main Contents
- Checkpoint read, create, finalize, and delete declarations.
- Checkpoint mode and snapshot query declarations.
- Checkpoint info/stat query declarations.
- Cpfile inode read declaration.

## Important Details
The API separates creating a checkpoint entry from finalizing it with root/ifile state, matching the segment construction workflow.

## Risks
Callers must serialize mutating checkpoint operations through the metadata transaction and cpfile locking expectations implemented in `cpfile.c`.
