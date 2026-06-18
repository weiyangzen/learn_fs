# File Research: sources/virtualization/libguestfs/daemon/df.c

Wraps `df` and `df -h`.

Key points:
- Both `do_df` and `do_df_h` require a root filesystem mounted via `NEED_ROOT`.
- Runs external `df` in the appliance context.
- Returns command stdout directly to caller.
- Errors are propagated from captured stderr.
