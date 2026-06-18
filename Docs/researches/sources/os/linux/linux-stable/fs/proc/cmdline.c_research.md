# File Research: sources/os/linux/linux-stable/fs/proc/cmdline.c

## Purpose

Creates `/proc/cmdline`, exposing the saved kernel command line.

## Main Responsibilities

- `cmdline_proc_show()` writes `saved_command_line` followed by a newline.
- `proc_cmdline_init()` creates a permanent single proc entry named `cmdline`.
- Sets the proc entry size to `saved_command_line_len + 1`.

## Notes

This is a small global proc entry initialized with `fs_initcall()`.
