# File Research: sources/virtualization/nvme-cli/libnvme/test/nbft/gen-nbft-diffs.sh.in

## Role

`gen-nbft-diffs.sh.in` is a Meson-configured helper for regenerating expected NBFT parser output files.

## Behavior

The script iterates over every file in `@TABLES_DIR@`, runs the configured `@NBFT_DUMP_PATH@` executable on it, and writes output to `@DIFF_DIR@/<table basename>`.

## Dependencies

- Substituted Meson variables: `TABLES_DIR`, `NBFT_DUMP_PATH`, and `DIFF_DIR`.
- POSIX shell.

## Filesystem/Storage Relevance

It maintains golden outputs for NVMe Boot Firmware Table parsing tests.
