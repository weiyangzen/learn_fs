# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/fstab.py

Simple `/etc/fstab` parser used to prefill mount options.

Key classes:
- `FSTab`
  - `refresh()` reads `/etc/fstab`, skips comments and malformed lines, stores `FSTabEntry` objects.
  - `get(device=None, label=None, uuid=None)` matches entries by raw device path, `LABEL=...`, or lowercase `UUID=...`.
- `FSTabEntry`
  - Stores `spec`, `mountpoint`, `vfstype`, `options`, `freq`, `passno`.
  - Builds a tab-separated string formatter from constructor arg names.
  - Normalizes UUID specs to lowercase.
  - Implements `__str__` and `__repr__`.

Usage:
- `mount.py` uses it to find default mountpoint/options for an OCFS2 device.

Notable details:
- Does not handle escaped whitespace in fstab fields.
- Blank lines fall through to split error and are ignored.
