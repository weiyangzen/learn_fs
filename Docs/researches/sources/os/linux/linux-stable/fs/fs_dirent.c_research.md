# File Research: sources/os/linux/linux-stable/fs/fs_dirent.c

This file provides small generic conversion helpers between filesystem on-disk file type values, Linux directory entry `DT_*` values, and inode mode bits.

Major responsibilities:
- Map `FT_*` on-disk filesystem file types to `DT_*` dirent file types.
- Map `DT_*` values to `FT_*` on-disk filesystem file types.
- Convert `umode_t` file modes to on-disk `FT_*` values.
- Convert `umode_t` file modes directly to `DT_*` values.

Important design points:
- Unknown or out-of-range on-disk file types degrade to `DT_UNKNOWN`.
- The `DT_*` to `FT_*` table is sparse; unspecified values default to `FT_UNKNOWN`.
- `fs_umode_to_ftype()` uses `S_DT(mode)` as the bridge from inode mode to dirent type.

Key invariants:
- `filetype >= FT_MAX` must not index the conversion table.
- Unsupported mode/type values are represented as unknown rather than guessed.
- Helpers are context-independent and perform no allocation or locking.

External interfaces:
- Exports GPL-only helpers `fs_ftype_to_dtype`, `fs_umode_to_ftype`, and `fs_umode_to_dtype`.
