# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/fdisk.c

## Purpose
Top-level driver for `fdisk`.

## Key Behavior
- Parses options for GPT/MBR initialization, GPT partition reinitialization, bootcode update, recovery, edit mode, geometry overrides, disk size override, boot partition template, default MBR file, verbosity, and assume-yes mode.
- Loads default MBR boot code from `_PATH_BOOTDIR "mbr"` when supported or from `-f`.
- Opens disk read-only for print-only mode or read-write for editing/initialization.
- Uses pledge profiles:
  - `stdio` for read-only print.
  - `stdio disklabel proc exec rpath` for editing/init/recovery/manual display.
- Initialization modes:
  - `-g`: create GPT.
  - `-A`: recreate GPT partition entries only.
  - `-i`: create MBR.
  - `-u`: update MBR boot code.
  - `-R`: recover GPT/MBR from disk or printed file.
- `parse_bootprt()` parses `blocks[@offset[:type]]`.
- `recover_disk_gpt()` attempts to recover GPT from disk primary/secondary structures.
- `recover_file_gpt()` and `recover_file_mbr()` reconstruct partition tables from printed `fdisk` output.
- `recover()` selects disk recovery or file recovery and falls back from GPT to MBR parsing.

## Notes
This file handles mode selection and safety prompts, while actual GPT/MBR mutation lives in dedicated modules.
