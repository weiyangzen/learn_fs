# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_stat.c

Read completely: 122 lines.

This implements old `stat`, `fstat`, and `lstat` returning `struct stat12`. Each calls the corresponding `*50` wrapper and converts native `stat` fields into the old layout, including 32-bit device/inode/rdev and 32-bit timestamp seconds.

Important interactions: `st_nlink` is saturated at `32767` if the native link count exceeds the old signed 15-bit range.

Security/reliability notes: field truncation/saturation are intentional compatibility behavior and can hide large native values from old callers.
