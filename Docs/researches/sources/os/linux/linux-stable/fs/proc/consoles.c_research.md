# File Research: sources/os/linux/linux-stable/fs/proc/consoles.c

## Purpose

Implements `/proc/consoles`, listing registered kernel consoles and their capabilities/flags/device numbers.

## Main Responsibilities

- `show_console_dev()` formats one console entry:
  - Console name and index.
  - Read/write/unblank capabilities.
  - Flags for enabled, preferred console, boot console, nbcon, printbuffer, braille, anytime.
  - Device major/minor when available from the console’s tty driver.
- Traverses consoles with seq operations:
  - `c_start()` locks the console list and advances to the requested offset.
  - `c_next()` advances through console hlist nodes.
  - `c_stop()` unlocks the console list.
- `proc_consoles_init()` creates the `consoles` seq proc entry.

## Concurrency Notes

- Holds `console_list_lock()` during seq traversal.
- Takes `console_lock()` around console `device()` callback to serialize with console operations such as vt switching.
