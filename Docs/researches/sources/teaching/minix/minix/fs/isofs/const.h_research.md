# File Research: sources/teaching/minix/minix/fs/isofs/const.h

This header defines ISO9660 constants and feature toggles.

Key constants:
- `GETDENTS_BUFSIZ`.
- ISO standard ID: `CD001`.
- Superblock/volume descriptor offset: `32768`.
- Minimum block size: `2048`.
- Fixed ISO9660 field sizes for IDs and timestamps.
- Maximum ISO and Rock Ridge file ID lengths.
- System UID/GID defaults.

Feature toggles:
- `ISO9660_OPTION_ROCKRIDGE` enabled.
- `ISO9660_OPTION_MODE3` present but disabled with TODO.

Role:
- Shared format constants for volume descriptor parsing, directory parsing, and Rock Ridge handling.
