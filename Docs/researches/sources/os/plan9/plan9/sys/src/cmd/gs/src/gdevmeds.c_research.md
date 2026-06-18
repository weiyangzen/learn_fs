# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmeds.c

Implements shared media selection support for printer drivers. The exported function is `select_medium`.

The file contains a static table of known media names with physical width, height, and priority. Priority is inverse area, so among acceptable media the smallest matching sheet/envelope is preferred.

`select_medium(gx_device_printer *pdev, const char **available, int default_index)` computes current page size in meters from device pixels and DPI, then scans the caller’s NULL-terminated available-media list. It returns the index of the smallest available medium whose dimensions exceed the page size within a 0.1 cm tolerance.

Supported names include ISO A/B sizes, ARCH sizes, letter/legal/ledger/executive/note, envelopes such as com10/dl/c5/monarch, and variants like flsa/flse.

This helper is used by printer drivers such as `gdevl31s.c` to map Ghostscript page size to device-specific media index tables.
