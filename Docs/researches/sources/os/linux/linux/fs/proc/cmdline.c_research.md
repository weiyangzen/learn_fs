# File Research: sources/os/linux/linux/fs/proc/cmdline.c

## Purpose
Creates `/proc/cmdline`, exposing the saved kernel command line.

## Main Responsibilities
- Implements a seq_file show callback that writes `saved_command_line` followed by newline.
- Registers a permanent single proc entry named `cmdline`.
- Sets proc entry size to `saved_command_line_len + 1`.

## Key Interfaces
- `cmdline_proc_show()`
- `proc_cmdline_init()`

## Dependencies and Integration
Uses procfs single-file helpers and global command-line state from proc internals/kernel init.

## Risks and Review Hotspots
- This is a stable userspace ABI file; output format changes would affect tooling.
- The proc entry is made permanent, so removal is not expected.
