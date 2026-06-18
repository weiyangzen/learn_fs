# File Research: sources/os/linux/linux-stable/fs/dlm/lvb_table.h

## Purpose
`lvb_table.h` declares the global lock-value-block transition table.

## Export
- `extern const int dlm_lvb_operations[8][8];`

## Use
The table is consumed by DLM lock/user/callback logic to decide how lock value blocks are copied, invalidated, or ignored across lock-mode transitions.

## Notes
This file is declaration-only.
