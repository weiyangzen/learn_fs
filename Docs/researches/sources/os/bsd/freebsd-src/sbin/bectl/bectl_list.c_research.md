# File Research: sources/os/bsd/freebsd-src/sbin/bectl/bectl_list.c

## Purpose
Implements `bectl list`, formatting boot environment, dataset, snapshot, active, mount, space, and creation-time information.

## Main Elements
- `struct printc`: carries column widths and display mode flags.
- `get_origin_props()`: fetches properties for a BE origin snapshot/dataset.
- `dataset_space()`: fetches `used` space for an origin dataset, truncating snapshot names as needed.
- `print_info()`: prints one BE/dataset/snapshot row, including active flags `N`, `R`, `T`, mountpoint, computed space, and creation time.
- `print_snapshots()`: prints snapshots for a dataset.
- `print_headers()`: computes column widths and prints headers unless script mode is selected.
- `prop_list_sort()`: sorts nvlist boot environments by string or numeric properties, supporting reverse order.
- `bectl_cmd_list()`: parses `-a`, `-D`, `-H`, `-s`, `-c`, `-C`; fetches BE props; sorts; prints rows.

## Dependencies And Integration
Uses libbe property-list APIs and nvlist iteration. Output feeds humans by default and scripts with `-H`.

## Risk Notes
Formatting depends on string properties returned by libbe. `-D` space composition is disabled when `-a` or `-s` expands rows, avoiding misleading combined totals.
