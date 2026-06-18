# File Research: sources/local-fs/mtd-utils/load_nandsim.sh

## Purpose
Loads the Linux `nandsim` module with ID bytes selected to emulate a supported NAND flash size, eraseblock size, and page size combination.

## Behavior
The script rejects execution if `/proc/mtd` already contains a NAND simulator. It accepts size in MiB plus optional eraseblock size in KiB and page size, defaulting to `16` KiB eraseblocks and `512` byte pages.

For 512-byte pages, it only permits 16 KiB eraseblocks and maps sizes 16, 32, 64, 128, and 256 MiB to two-byte NAND IDs. For 2048-byte pages, it maps eraseblock sizes 64, 128, 256, or 512 KiB plus sizes 64 through 1024 MiB to four ID bytes.

## Dependencies
Requires `/proc/mtd`, `grep`, and root/module privileges for `modprobe nandsim`.

## Risks and Notes
The script runs with `set -euf`, but it assigns `eb_size="$2"` and `page_size="$3"` before checking whether optional arguments exist. With only the mandatory size argument, `set -u` can abort before defaults are applied.
