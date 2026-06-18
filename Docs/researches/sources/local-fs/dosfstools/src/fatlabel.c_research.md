# File Research: sources/local-fs/dosfstools/src/fatlabel.c

Command-line interface for displaying/changing FAT volume label or serial number.

Main flow:
- Defines the same global knobs required by shared fsck/label code: `rw`, `list`, `test`, `verbose`, `fat_table`, `n_files`, `mem_queue`, etc.
- Parses options:
  - `-i/--volume-id`
  - `-r/--reset`
  - `-c/--codepage`
  - `-V/--version`
  - `-h/--help`
- Initializes Atari variant detection and DOS codepage conversion.
- Chooses read-write mode only for change/reset operations.
- `handle_label()`:
  - validates new labels, converts local text to DOS codepage, pads to 11 bytes
  - opens filesystem, reads boot sector
  - reads FAT only for FAT32 when root-directory traversal needs cluster chains
  - prints existing label, writes new label, or removes label.
- `handle_volid()`:
  - validates hexadecimal 32-bit serial input
  - resets serial using `generate_volume_id()` when requested
  - reads/writes boot serial.

Dependencies:
- Reuses `fs_open`, `read_boot`, `read_fat`, `find_volume_de`, `write_label`, `remove_label`, `write_serial`, `pretty_label`, and char conversion helpers.

Research notes:
- This command does not perform full fsck repair; it uses only enough FAT support to locate root label entries on FAT32.
