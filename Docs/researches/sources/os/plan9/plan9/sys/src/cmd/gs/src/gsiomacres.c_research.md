# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsiomacres.c

Implements `%macresource%`, an IODevice for loading MacOS font resources from resource forks or `.dfont` data forks.

Resource parsing:
- Defines resource header, resource entry, and resource list structures.
- Reads big-endian 32-, 24-, 16-, and 8-bit values.
- Parses resource map type lists, reference lists, names, flags, offsets, and lengths.
- Loads requested resource data into memory.

IODevice behavior:
- Expects names of the form `path#type+id`.
- Parses the four-character resource type and numeric id.
- First tries `gp_read_macresource` for the resource fork.
- If that fails, tries `read_datafork_resource` for serialized data-fork resources.
- Allocates a Ghostscript string buffer and exposes it through a read stream.

Risks and quirks:
- Uses raw `malloc`/`free` for parser data, not Ghostscript memory.
- Several allocation and read-error paths leak intermediate parser allocations.
- `read_int8` stores `fgetc` into a byte and checks `< 0`, which is fragile for EOF.
- Only open-file is implemented; delete, rename, status, and enumeration are unsupported.
