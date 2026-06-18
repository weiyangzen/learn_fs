# File Research: sources/os/bsd/freebsd-src/sbin/swapon/swapon.c

## Summary
Implements `swapon`, `swapoff`, and `swapctl`. It activates/deactivates swap devices or files, processes fstab entries, supports md-backed and GELI-encrypted swap setup, optionally trims devices before activation, and lists swap usage through sysctl.

## Main Responsibilities
- Selects behavior from invocation name or `swapctl` options.
- Supports all-fstab activation/deactivation, late swap filtering, quiet mode, forced swapoff, alternate fstab, and human/block-size listing.
- Parses fstab swap entries while skipping `noauto` and honoring `late`.
- Handles plain special files with `swapon()`/`swapoff()`.
- Handles GELI `.eli` devices by running `geli onetime` before activation.
- Handles md-backed swap with `file=` fstab options by running `mdconfig` attach/list/detach.
- Supports md device forms such as `md`, `/dev/md`, `mdN`, `/dev/mdN`, and `.eli` variants.
- Builds GELI arguments from fstab options: `aalgo`, `ealgo`, `keylen`, `sectorsize`, `notrim`, and `trimonce`.
- Implements one-time trim with `DIOCGDELETE` before `swapon()`.
- Lists swap devices and totals using `vm.swap_info` sysctl entries.

## Key Elements
- `swap_on_off()`: dispatches md, GELI, or plain special-file handling.
- `swap_on_off_md()`: creates/finds/destroys vnode-backed md devices around swap activation/deactivation.
- `swap_on_off_geli()` and `swap_on_geli_args()`: one-time encryption setup.
- `run_cmd()`: fork/exec helper for `mdconfig` and `geli`, with optional stdout pipe.
- `swapon_trim()`: trims data area while keeping the device open through swap activation.
- `swaplist()`: implements `swapctl -l/-s` listing.
- `sizetobuf()`: block-size and human-readable formatting helper.

## Dependencies And Integration
Uses `fstab`, `mdconfig`, `geli`, `swapon(2)`, `swapoff(2)`, disk ioctls, `vm.swap_info`, `devname()`, and libutil formatting helpers.

## Research Notes
`run_cmd()` constructs command strings then splits only on spaces, so helper arguments containing spaces are not shell-quoted. The current callers mostly pass device paths and option fragments expected not to contain spaces.
