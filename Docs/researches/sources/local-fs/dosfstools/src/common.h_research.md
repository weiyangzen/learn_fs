# File Research: sources/local-fs/dosfstools/src/common.h

Shared declarations for utilities, globals, and FAT variant state.

Contents:
- Defines fallback `OFF_MAX`.
- Declares global modes:
  - `interactive`
  - `write_immed`
  - `atari_format`
  - `program_name`
- Declares fatal diagnostics, allocation helpers, queued allocation cleanup, `xasprintf`, interactive choice/input helpers, Atari detection, volume ID generation, and volume-label validation.

Role:
- Provides common infrastructure used across fsck, fatlabel, boot parsing, FAT repair, file operations, and I/O.
