# File Research: sources/os/linux/linux/fs/dlm/lvb_table.h

## Role

`lvb_table.h` declares the global `dlm_lvb_operations[8][8]` table.

## Function

The table is used by DLM user/callback paths to determine lock value block behavior across lock mode transitions.

## Research Notes

Read completely. The file is declaration-only and depends on the implementation of the table elsewhere in the DLM subsystem.
