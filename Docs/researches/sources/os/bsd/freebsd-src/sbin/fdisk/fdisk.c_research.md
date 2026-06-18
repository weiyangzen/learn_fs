# File Research: sources/os/bsd/freebsd-src/sbin/fdisk/fdisk.c

Implements deprecated FreeBSD MBR partition editor `fdisk`.

Key responsibilities:
- Prints a deprecation warning recommending `gpart`.
- Opens a target disk with `libgeom`.
- Detects media sector size by probing reads.
- Reads and writes MBR sector zero, including boot code and four DOS partition entries.
- Prints summary/configuration output.
- Initializes a whole-disk FreeBSD MBR slice with `-I`.
- Supports interactive partition editing, active partition selection, and boot code replacement.
- Supports non-interactive config files through `-f`.
- Infers root disk when no disk argument is supplied.

Important data:
- `struct mboot`: boot code buffer/size and decoded `struct dos_partition parts[4]`.
- Geometry globals: real and DOS/BIOS cylinders, heads, sectors, sectors per cylinder.
- Global option flags for `-B`, `-I`, `-a`, `-b`, `-f`, `-i`, `-p`, `-q`, `-s`, `-t`, `-u`, `-v`.
- `part_types[256]`: static MBR partition type descriptions.

Core functions:
- `get_params()` obtains firmware heads/sectors and media size through disk ioctls/libgeom.
- `read_s0()` validates MBR signature and decodes partition entries with `dos_partition_dec()`.
- `write_s0()` encodes partition entries and writes boot sectors.
- `init_boot()` reads boot code, default `/boot/mbr`.
- `init_sector0()` initializes boot code plus a FreeBSD partition.
- `change_part()`, `change_active()`, `change_code()` implement interactive modification.
- `dos()` converts LBA start/size into legacy CHS fields.
- `parse_config_line()`, `process_geometry()`, `process_partition()`, `process_active()`, and `read_config()` implement config-file mode.
- `sanitize_partition()` warns and optionally adjusts alignment.
- `get_rootdisk()` derives a whole-disk device from `/` mount source, stripping `.eli` and `.journal`.

Config file syntax:
- `g c<CYL> h<HEADS> s<SECTORS>`
- `p <partition> <type> <start|*> <size|*>`
- `a <partition>`

Risks and constraints:
- Deprecated and unavailable in FreeBSD 16 or later per runtime warning.
- MBR/BIOS CHS assumptions are legacy and can be invalid for modern disks.
- `read_disk()` and `write_disk()` seek using `sector * 512` even while supporting variable `secsize`; the file comments acknowledge hardcoded sector-size behavior in write path.
- Many interactive inputs use simple decimal parsing and prompts, fitting legacy admin tooling rather than robust batch validation.
