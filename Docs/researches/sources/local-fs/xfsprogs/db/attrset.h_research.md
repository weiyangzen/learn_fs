# File Research: sources/local-fs/xfsprogs/db/attrset.h

## Scope

Minimal declaration header for expert-mode attribute mutation/listing commands.

## API

- Declares `attrset_init()`.

## Dependencies And Role

- Used by xfs_db initialization code to register attrset commands when expert mode permits them.
- Command implementation and helper details remain private to `attrset.c`.

## Risks

- The small exported surface keeps mutation commands centralized in one implementation file.
