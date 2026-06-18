# File Research: sources/local-fs/dosfstools/src/fsck.fat.c

Main command-line driver for `fsck.fat`.

Main flow:
- Sets terminal to noncanonical/no-echo mode for single-key interactive choices, restoring at exit.
- Initializes globals: read-write mode, interactivity, list/test/verbose flags, FAT table choice, label policy, memory queue.
- Parses options for auto repair, Atari variant, boot-only check, codepage, drop/undelete, salvage, FAT table selection, listing, read-only, interactive repair, name policy, bad-cluster test, uppercase labels, verbose, verification pass, immediate writes, and long `--variant`.
- Opens target with `fs_open()`.
- Calls `read_boot()`.
- If not boot-only:
  - loops `read_fat(..., repair mode)` and `scan_root()` until stable
  - checks labels
  - optionally marks bad clusters
  - either salvages unowned chains to files or frees them
  - checks dirty bits
  - updates free-cluster summary
  - reports unused drop/undelete requests
  - optionally runs verification pass.
- Prompts whether to write queued changes unless immediate writes are enabled.
- Prints final file/cluster summary.
- Returns `1` if filesystem changed, otherwise `0`.

Dependencies:
- This is orchestration only; substantive repair is delegated to `boot.c`, `fat.c`, `check.c`, `file.c`, and `io.c`.

Research notes:
- Automatic modes `-a`, `-p`, and `-y` enable noninteractive repair and salvage.
- `-n` disables writes and interactivity.
- `-t` and `-w` are rejected in read-only mode.
