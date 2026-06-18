# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/atexit.c

## Purpose
Provides libext2fs-managed normal-exit cleanup callbacks.

## Main Elements
- `struct exit_data`: callback plus opaque data.
- Static `items` and `nr_items`: process-global callback list.
- `handle_exit()`: registered with libc `atexit()`, calls callbacks in reverse registration order, skips null entries, frees storage.
- `ext2fs_add_exit_fn()`: adds a unique callback/data pair, reuses null slots, registers `handle_exit()` on first use, and resizes storage.
- `ext2fs_remove_exit_fn()`: removes matching callback/data by shifting entries and clearing the tail.

## Dependencies And Integration
Uses libext2fs memory resize/free helpers. Intended for normal process termination cleanup; comments state signal exits must call `exit()` themselves if these callbacks are required.

## Risk Notes
The callback list is process-global and not synchronized. `handle_exit()` computes `items + nr_items - 1`; with `nr_items == 0` it is only reached after registration, but direct misuse would be unsafe.
