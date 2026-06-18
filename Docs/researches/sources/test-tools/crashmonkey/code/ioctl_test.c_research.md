# sources/test-tools/crashmonkey/code/ioctl_test.c

Purpose: small user-space smoke test that opens a cow_brd snapshot device and issues a restore ioctl.

Important APIs/control flow: `main()` opens `/dev/cow_ram_snapshot1_0`, calls `ioctl(fd, COW_BRD_RESTORE_SNAPSHOT)`, prints simple errors, closes the fd, and returns the ioctl result or negative error sentinel.

State and persistence behavior: restore mutates the cow_brd snapshot state by reverting it to the saved baseline. The program itself stores no persistent state.

Dependencies and integration: includes `disk_wrapper_ioctl.h` for the cow_brd ioctl number and assumes the cow_brd module/device already exists.

Risks: hard-coded device path, missing `stdio.h` and `unistd.h` includes for `printf()`/`close()` in strict builds, no command-line configurability, and overlapping ioctl numbers with wrapper commands.

Test signals: success is process exit `0`; open/ioctl failure prints a short message and returns negative values.
