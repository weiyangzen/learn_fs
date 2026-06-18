# File Research: sources/virtualization/nbdkit/filters/extentlist/extentlist.c

Implements an extent metadata override filter. The required `extentlist=<file>` parameter points to a text file containing offset, length, and optional type fields.

At get-ready time, `parse_extentlist()` reads the file completely, skips blank/comment lines, parses sizes with `nbdkit_parse_size()`, accepts numeric extent type values or strings containing `hole`/`zero`, sorts by offset, rejects overlaps and overflow, then fills all gaps with `HOLE|ZERO` synthetic extents. A trailing hole extent extends coverage to `UINT64_MAX`.

`extentlist_extents()` binary-searches the normalized list for the requested offset and emits consecutive extents with `nbdkit_add_extent()` until the requested count is covered. The filter always advertises extents support.

The source is intentionally metadata-only; it does not alter reads or writes.
