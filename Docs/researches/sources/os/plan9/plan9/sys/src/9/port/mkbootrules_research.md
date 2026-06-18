# File Research: sources/os/plan9/plan9/sys/src/9/port/mkbootrules

Purpose: rc/awk build helper that generates mk rules for embedding boot directory files as root images.

Key logic:
- Reads kernel config sections and collects entries under `bootdir`.
- Produces rules for `$CONF.root.s` using `../port/mkrootall`.
- Produces rules for `$CONF.rootc.c` using `../port/mkrootc`.
- Sanitizes file paths into C symbol names by replacing non-alphanumeric/underscore characters.

Dependencies and integration:
- Uses `rc`, `awk`, `$objtype`, `$CONF`, and kernel config file format.

Risks and notes:
- Assumes `bootdir` section indentation and section-boundary conventions.
