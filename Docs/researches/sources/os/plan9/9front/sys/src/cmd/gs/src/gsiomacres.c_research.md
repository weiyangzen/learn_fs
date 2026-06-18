# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsiomacres.c

## Role

`gsiomacres.c` implements the `%macresource%` IODevice used to load MacOS font resources from resource forks or `.dfont` data forks into Ghostscript streams.

This is Ghostscript IODevice/resource parsing code with host file access, not a filesystem implementation.

## Main Interfaces

- Device definition: `gs_iodev_macresource`.
- Device operations: `iodev_macresource_init`, `iodev_macresource_open_file`.
- Resource parsing helpers: big-endian integer readers, `res_string2type`, `res_type2string`, `read_resource_header`, `read_resource_map`, `load_resource`, `read_datafork_resource`.

## Core Behavior

- File names are expected to include a resource selector suffix: `#<type>+<id>`.
- The device first tries platform `gp_read_macresource` for a resource fork. If that fails, it treats the file as a serialized data-fork resource map (`.dfont`).
- For data forks, it reads the resource header, resource map, type list, reference records, optional Pascal names, and then loads the requested resource data by type/id.
- On success, it allocates a Ghostscript buffer, copies the resource data into it, creates a read-string stream, and returns that stream.

## Notable Risks

- The parser uses C `malloc` for headers, lists, resource names, and data and does not consistently free all allocations on success/error paths.
- Several reads do not validate short reads or buffer bounds after the map header is loaded.
- `read_int8` stores `fgetc` into a `byte`, then checks `c < 0`; EOF detection is ineffective if `byte` is unsigned.
- `strncpy(filename, fname, min(namelen, gp_file_name_sizeof))` may leave `filename` unterminated when `namelen >= gp_file_name_sizeof`.
- Type strings are assumed to be at least four bytes.
