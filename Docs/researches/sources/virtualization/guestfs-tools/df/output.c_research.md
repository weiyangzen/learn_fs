# File Research: sources/virtualization/guestfs-tools/df/output.c

## Scope

Output formatting for `virt-df`.

## Behavior

- `print_title` emits text or CSV headers for block or inode mode.
- `print_stat` canonicalizes device names, computes block/inode totals, used/free values, and percentages.
- Non-human block mode scales filesystem block counts to 1K units.
- Human mode uses gnulib `human_readable` with base-1024 SI formatting.
- Text mode combines guest name and filesystem as `name:dev`, aligning or wrapping long names.
- CSV mode writes name, device, and four stat columns as separate escaped fields.
- UUID mode replaces name with UUID when available.
- Percentages emulate `df` with ceil in text mode and one decimal in CSV mode.

## Dependencies And Risks

- Exits on failure to canonicalize device name or write output.
- CSV escaping is local and handles spaces, quotes, newlines, and commas.
- `human` and `csv` are expected to be mutually exclusive, enforced by `main.c`.
