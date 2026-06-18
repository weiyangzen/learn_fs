<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_struct_stat.c -->
# sources/test-tools/strace/src/print_struct_stat.c

Purpose: prints normalized file status structures.

Important APIs/types/functions: `print_struct_stat`, `struct strace_stat`, device/inode/mode/uid/gid/time field printers, and macro remapping from `st_*` names to normalized fields.

Control flow: prints common stat fields including device, inode, mode, link count, uid/gid, rdev, size, block size, blocks, and timestamps. Nanosecond fields are printed when `has_nsec` is set; otherwise timestamps still get human-readable time comments.

State and persistence behavior: no state.

Dependencies and integration points: shared by old/new stat fetchers and syscall decoders; depends on `stat.h`, device/mode/uid/time printers, and field macros.

Risks: normalized `strace_stat` must be populated correctly by fetchers. Conditional nanosecond output affects golden traces.

Test signals: stat family syscalls with regular files/devices, nanosecond and non-nanosecond layouts, invalid pointers, large inode/size values, and mode/uid/gid formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_struct_stat.c -->
