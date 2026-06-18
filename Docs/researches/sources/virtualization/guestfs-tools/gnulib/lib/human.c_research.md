# File Research: sources/virtualization/guestfs-tools/gnulib/lib/human.c

Human-readable size formatting and block-size option parsing.

Main functions:
- `human_readable`: converts a `uintmax_t` quantity from one block size to another with rounding, grouping, autoscaling, and SI suffix options.
- `human_options`: parses block-size specifications into options and block size.

Formatting behavior:
- Uses exact integer arithmetic where possible.
- Falls back to `long double` when exact integer scaling is not straightforward.
- Supports rounding styles: ceiling, nearest, floor.
- Supports locale decimal point, grouping, and thousands separators.
- Supports base 1000 or base 1024, suffixes up to Y/yotta-style scale, optional `B`/`iB`.

Parsing behavior:
- Reads explicit spec or environment variables `BLOCK_SIZE` / `BLOCKSIZE`.
- Defaults to `512` under `POSIXLY_CORRECT`, otherwise `DEFAULT_BLOCK_SIZE` of `1024`.
- Uses `argmatch` for `human-readable` and `si`.
- Uses `xstrtoumax` for numeric suffix parsing.

Research relevance: used by `virt-filesystems -h` and similar tools for stable size presentation.
