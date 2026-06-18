# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/misc.c

General utility code for the Ext2Fsd driver. It provides small arithmetic/time helpers, filename character-set conversion wrappers, sleep, Windows-to-Linux error translation, Linux-to-Windows status translation, and dot/dotdot name checks.

`Ext2Log2` returns the zero-based order of a positive value by shifting until zero. `Ext2NtTime` converts Unix seconds-since-1970 to NT time, while `Ext2LinuxTime` converts an NT `LARGE_INTEGER` back to Unix seconds and falls back to the current system time if conversion fails.

The filename conversion helpers bridge the driver’s optional Linux NLS tables with Windows RTL OEM conversion. `Ext2MbsToUnicode` and `Ext2UnicodeToMbs` first count output length by calling a selected `nls_table`’s `char2uni` or `uni2char`, then optionally fill the caller’s buffer after checking capacity. `Ext2OEMToUnicodeSize`, `Ext2OEMToUnicode`, `Ext2UnicodeToOEMSize`, and `Ext2UnicodeToOEM` prefer the configured VCB codepage table, then fall back to `RtlOemStringToCountedUnicodeSize`, `RtlOemStringToUnicodeString`, `RtlxUnicodeStringToOemSize`, or `RtlUnicodeStringToOemString`.

`Ext2Sleep` delays the current kernel thread for the requested milliseconds. `Ext2LinuxError` maps many `NTSTATUS` values to negative Linux `errno` values used by the Linux-derived ext2/ext3 code. `Ext2WinntError` maps common negative Linux errors back to Windows status codes. `Ext2IsDot` and `Ext2IsDotDot` recognize Unicode `"."` and `".."` directory names by exact byte length and character contents.
