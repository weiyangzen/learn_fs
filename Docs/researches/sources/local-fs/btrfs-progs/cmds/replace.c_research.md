# File Research: sources/local-fs/btrfs-progs/cmds/replace.c

## Purpose

Implements the `btrfs replace` command group for live device replacement: starting a replace operation, monitoring status, and canceling an active operation.

## Commands Implemented

- `replace start [-BfrK] [--enqueue] <srcdev>|<devid> <targetdev> <mount_point>`
- `replace status [-1] <mount_point>`
- `replace cancel <mount_point>`

## Key Helpers

- `replace_dev_result2string()` maps kernel replace result codes to user-readable strings.
- `dev_replace_sigint_handler()` cancels an active replace on SIGINT.
- `dev_replace_handle_sigint()` installs or restores SIGINT handling.
- `print_replace_status()` polls `BTRFS_IOCTL_DEV_REPLACE_CMD_STATUS` and prints progress or final state.
- `time2string()` formats kernel timestamps.
- `progress2string()` formats progress in tenths of a percent.

## Replace Start Flow

`cmd_replace_start()`:

1. Parses options:
   - `-B`: do not background.
   - `-r`: avoid reading from source if another good mirror exists.
   - `-f`: force target device use.
   - `--enqueue`: wait for another exclusive operation.
   - `-K, --nodiscard`: skip whole-device trim.
2. Opens the mounted filesystem.
3. Reads filesystem feature flags and detects zoned mode.
4. Checks exclusive-operation state.
5. Queries current replace status and rejects already-started replace.
6. Resolves source as either devid or block-device path.
7. Validates target device with mkfs safety checks.
8. Verifies target size is at least source size.
9. Opens and prepares the target device, with optional discard and zoned preparation.
10. Installs SIGINT cancel handler.
11. Backgrounds unless `-B` is set.
12. Starts replace through `BTRFS_IOC_DEV_REPLACE`.

## Status Behavior

`replace status` prints:

- running progress
- finished/canceled/suspended times
- write error count
- uncorrectable read error count

Without `-1`, it refreshes once per second until the operation reaches a terminal state.

## Cancel Behavior

`replace cancel` sends `BTRFS_IOCTL_DEV_REPLACE_CMD_CANCEL`. If no replace was started, it prints informational output and returns status `2`.

## External Interfaces

Uses:

- `BTRFS_IOC_GET_FEATURES`
- `BTRFS_IOC_DEV_REPLACE`
- filesystem exclusive-operation checks
- device size/probing/preparation helpers from common device and mkfs code

## Important Behavior

- Source may be specified as a device ID when the original source device is missing.
- Mounted target devices are protected by `test_dev_for_mkfs`.
- RAID5/6 unsupported-kernel cases are surfaced with a specific warning on `EOPNOTSUPP`.
- The start command may daemonize before issuing the start ioctl unless `-B` is used.
