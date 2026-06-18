# File Research: sources/local-fs/btrfs-progs/cmds/balance.c

## Purpose
Implements the `btrfs balance` command group: start, pause, cancel, resume, status, and hidden legacy full-balance behavior.

## Parsing and Validation
- `parse_one_filter()` handles balance filters: `profiles`, `usage`, `devid`, `drange`, `vrange`, `convert`, `soft`, `limit`, and `stripes`.
- `parse_filters()` splits comma-separated filter strings for data/system/metadata scopes.
- Duplicate filters produce warnings; invalid profiles, ranges, usage percentages, missing arguments, and unsupported filter combinations fail early.
- `drange` requires `devid`, and `soft` requires a matching `convert`.

## Balance Execution
- `cmd_balance_start()` builds `struct btrfs_ioctl_balance_args`, applies type flags, mirrors metadata filters to system chunks unless system is explicitly forced, and invokes `do_balance()`.
- `do_balance()` opens the mount directory, checks exclusive-operation state, calls `BTRFS_IOC_BALANCE_V2`, and falls back to old `BTRFS_IOC_BALANCE` only if no filters require v2.
- Background mode double-forks, detaches, redirects stdio to `/dev/null`, and then runs the balance.

## Safety Behavior
- Full unfiltered balance warns and delays unless `--full-balance` is used.
- Conversion with missing devices warns because new chunks could target failed devices.
- RAID5/6 conversion warns and delays unless `--force` is used.
- Explicit system-chunk balancing is refused unless forced.

## Other Commands
- `pause` and `cancel` call `BTRFS_IOC_BALANCE_CTL`.
- `resume` calls `BTRFS_IOC_BALANCE_V2` with `BTRFS_BALANCE_RESUME`.
- `status` calls `BTRFS_IOC_BALANCE_PROGRESS`, prints running/paused state and progress, and optionally dumps ioctl arguments.

## Registration
Defines the `balance` command group with start, pause, cancel, resume, status, and hidden `--full-balance`.
