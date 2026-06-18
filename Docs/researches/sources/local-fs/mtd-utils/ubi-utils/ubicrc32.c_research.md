# File Research: sources/local-fs/mtd-utils/ubi-utils/ubicrc32.c

## Role
CLI tool to calculate UBI-style CRC32 over a file or stdin.

## Main Behavior
- Opens the first positional argument as input, or reads stdin if no file is provided.
- Parses help/version options.
- Reads in 4096-byte chunks and updates CRC using initial value `UBI_CRC32_INIT`.
- Prints the CRC as `0x%08x`.

## Interfaces And Dependencies
- Uses `mtd_crc32` from `crc32.h`.
- Uses UBI media constant `UBI_CRC32_INIT`.

## Notes
- Opens `argv[1]` before option parsing, so option-only invocations like `-h` can be treated as filenames before help parsing.
- Opens files with mode `"r"` rather than binary mode; on Linux this is equivalent.
