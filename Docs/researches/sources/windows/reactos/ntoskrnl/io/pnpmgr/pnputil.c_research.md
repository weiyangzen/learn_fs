# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/pnputil.c

Read status: complete file, 195 lines.

This file contains small PnP utility routines for converting registry strings into kernel string objects and freeing those converted lists.

Key entry points:
- `PnpFreeUnicodeStringList()` frees each allocated string buffer in an array and then frees the array.
- `PnpRegMultiSzToUnicodeStrings()` validates a `REG_MULTI_SZ`, counts component strings, allocates a `UNICODE_STRING` array, copies each string into its own null-terminated buffer, and returns the count.
- `PnpRegSzToString()` scans a `REG_SZ` byte range for the first null terminator and optionally returns the string length in bytes.

Important dependencies:
- Registry value layout through `KEY_VALUE_FULL_INFORMATION`.
- Pool allocation tags `'sUpP'` and general pool freeing.

Notable behavior and risks:
- `PnpRegMultiSzToUnicodeStrings()` handles both double-null-terminated and length-bounded final strings.
- The allocated `UNICODE_STRING` array is not zero-initialized before individual buffers are filled. Error cleanup passes the number of completed entries, which avoids freeing uninitialized later entries.
- `PnpRegSzToString()` always returns `TRUE`; it reports a bounded length even if the input lacks a terminator.
