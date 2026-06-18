# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfslabel.c

## Role

`ntfslabel.c` implements the `ntfslabel` utility. It displays or changes an NTFS volume label, and can also display or change the boot-sector volume serial number.

## Command-Line Contract

Supported options include:

- Positional `device [label]`.
- `--new-serial[=hex]` and `--new-half-serial[=hex]`.
- `-n/--no-action`.
- `-f/--force`.
- `-q`, `-v`, `-V`, `-h`.

The short option string includes `I` and `i` internally for serial options, but usage presents them as long options.

## Control Flow

1. `parse_options()` captures the device, optional label, force/no-action/logging flags, and optional serial override.
2. `main()` refuses modifications to mounted devices unless forced or no-action.
3. If no label and no serial operation is requested, it forces read-only/no-action mode.
4. The volume is mounted with read-only when no-action and with recovery when forced.
5. Serial handling runs first:
   - `set_new_serial()` changes primary and backup boot-sector serials.
   - verbose mode without serial change prints the serial.
6. Label handling then either calls `change_label()` or `print_label()`.
7. The volume is unmounted without requesting dirty cleanup.

## Label Handling

`change_label()` converts the input label to NTFS Unicode with `ntfs_mbstoucs()`, truncates labels longer than 128 UTF-16 characters, and calls `ntfs_volume_rename()` unless no-action is set.

## Serial Handling

`set_new_serial()` either uses the provided hex serial or generates a random 64-bit value using `random()` seeded with time and PID. `change_serial()` writes the primary boot sector, then writes the backup boot sector only if it matches the saved original primary sector. The half-serial mode preserves the lower 32 bits.

## Risk Areas

- Bad serial hex input logs an error but does not increment the parse error count, so malformed serial arguments may still proceed with a parsed partial value.
- Backup boot-sector serial changes are skipped if the backup does not match the primary, which avoids overwriting divergent backup data but can leave serials inconsistent.
- `print_label()` warns when the target is mounted read-write because results may be unreliable.
- Forced writes to mounted devices are allowed with `--force` and can race with an active filesystem.
