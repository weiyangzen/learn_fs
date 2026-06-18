# File Research: sources/virtualization/nvme-cli/libnvme/test/nbft/nbft-dump-diff.sh.in

## Role

`nbft-dump-diff.sh.in` is a Meson-configured wrapper that compares one NBFT table’s parsed output with its expected diff fixture.

## Behavior

It requires two arguments: `TABLE` and `DIFF`. If the argument count is wrong it prints usage and exits `255`. Otherwise it runs `@NBFT_DUMP_PATH@ TABLE` and pipes stdout into `diff -u DIFF -`.

## Dependencies

- Substituted Meson variable `NBFT_DUMP_PATH`.
- POSIX shell and `diff`.

## Filesystem/Storage Relevance

It is test glue for validating deterministic parsing of NVMe boot firmware metadata.
