# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/afterpass1_common.h

## Purpose
Declares common cleanup callbacks used after fsck pass 1.

## Main Elements
- Prototypes for deleting metadata, leaf, data, EA indirect/leaf/entry/extentry blocks.
- Declares `remove_dentry_from_dir()`.

## Dependencies And Integration
Includes `util.h` and `metawalk.h`, exposing functions shaped for metawalk callbacks.

## Risk Notes
The declared callbacks mutate filesystem state; callers must provide correct fsck context and metawalk private data.
