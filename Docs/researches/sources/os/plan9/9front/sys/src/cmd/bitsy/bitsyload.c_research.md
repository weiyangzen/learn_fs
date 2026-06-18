# File Research: sources/os/plan9/9front/sys/src/cmd/bitsy/bitsyload.c

This utility writes Bitsy images into flash partitions.

Behavior:
- Method table maps verbs to partitions and default source files:
  - `k` -> `/dev/flash/kernel`
  - `r` -> `/dev/flash/ramdisk`
  - `u` -> `/dev/flash/user`
- Opens the target partition and `<partition>ctl`.
- Reads flash geometry from the control file.
- Reads the whole input file, pads to sector size, erases the partition, then writes sector-sized chunks.

Notable implementation details:
- Validates sector count and sector size before writing.
- Checks that padded input fits in the flash partition.
- `leputl` exists but is unused in this file.

Risks and caveats:
- Whole image is loaded into memory.
- Destructive operation: erases target flash partition before writing.
