# File Research: sources/os/bsd/freebsd-src/sbin/zfsbootcfg/zfsbootcfg.c

## Purpose
Manipulates ZFS boot environment boot configuration data through libzfsbootenv.

## Main Elements
- `add_pair()` fetches a bootenv nvlist, converts a string value to the requested nvpair type, adds the pair, writes the nvlist back, and frees it.
- Supports string, signed/unsigned 8/16/32/64-bit integers, byte, and boolean-value types.
- `delete_pair()` removes a key from a bootenv nvlist and writes it back.
- `main()` parses `-d`, `-k`, `-n`, `-p`, `-t`, `-v`, and `-z`.
- Defaults pool name from `kenv("vfs.root.mountfrom")` when `-z` is omitted and root is ZFS.
- If key is missing or key is `command`, uses `lzbe_set_boot_device()`; otherwise updates a named nvlist pair.
- Without mutations or `-p`, prints the current boot device in `zfs:<dataset>:` form.
- `-p` prints the bootenv or selected nvlist.

## Dependencies And Integration
Uses kernel environment, libzfsbootenv nvlist helpers, and ZFS bootenv conventions.

## Risk Notes
Value parsing checks full-string numeric conversion. Boolean parsing has sequential case-insensitive checks for YES/NO/true/false.
