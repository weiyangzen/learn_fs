# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/version.c

Exports version information for the bundled blkid snapshot.

Key constants:
- `E2FSPROGS_VERSION "1.37"`
- `E2FSPROGS_DATE "21-Mar-2005"`

Key functions:
- `blkid_parse_version_string(ver_string)`
  - Parses digits from version string, ignoring dots until first non-digit/non-dot.
  - Example: `1.37` becomes `137`.
- `blkid_get_library_version(ver_string, date_string)`
  - Optionally returns static version/date strings.
  - Returns parsed integer version.

Notable details:
- Copyright header says GNU Public License rather than LGPL, unlike most bundled blkid files.
