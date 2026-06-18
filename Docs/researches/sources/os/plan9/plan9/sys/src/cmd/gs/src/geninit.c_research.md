# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/geninit.c

Read status: complete.

Purpose: build-time utility that merges Ghostscript initialization PostScript files into a single PostScript file or a C byte array.

Inputs and outputs:
- Usage: `geninit [-(I|i) prefix] gs_init.ps gconfig.h gs_xinit.ps`.
- Or emits C with `-c`.
- Reads `gconfig.h` to discover `psfile_("...")` entries for `INITFILES`.

Main logic:
- `prefix_open` opens files under an optional library prefix, with Mac path translation under `__MACOS__`.
- `rl` reads lines while normalizing Unix, Mac, and DOS line endings.
- `doit` strips comments and whitespace outside string literals unless an included file is marked intact.
- `mergefile` processes special `%% Replace` directives, recursively includes named files, expands `INITFILES`, stops at `currentfile closefile`, and merges/minifies PostScript.
- `hex_string_to_binary` converts ASCII hex strings into binary object tokens for object-format sections.
- `merge_to_c` writes `const unsigned char gs_init_string[]`.
- `merge_to_ps` writes merged PostScript output.

Filesystem/storage relevance:
- Reads multiple initialization/config files and writes merged generated output.
- Handles path-prefixing and platform path translation.

Notable behavior and risks:
- Uses fixed `LINE_SIZE` of 128 for file names and lines.
- Relies on exact `psfile_("...")` formatting in generated config.
- Uses in-place mutation of line buffers while stripping comments/whitespace.
