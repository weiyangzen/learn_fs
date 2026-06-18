# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ipwidget.py

IPv4 address editor widget adapted from older Red Hat/Anaconda code.

Key functions/classes:
- `sanityCheckIPString(ip_string)`
  - Regex-validates four decimal octets.
  - Ensures each octet is 0-255.
- Exceptions:
  - `IPError`
  - `IPMissing`
- `IPEditor(gtk.HBox)`
  - Four 3-character `gtk.Entry` widgets separated by dots.
  - Numeric input only.
  - Typing `.` moves focus to next octet.
  - `hydrate(ip_string)` fills entries from a valid IP.
  - `dehydrate()` validates and returns dotted string.
  - Aliases:
    - `get_text = dehydrate`
    - `set_text = hydrate`

Validation behavior:
- Empty all fields raises `IPMissing`.
- First octet must be 1-255.
- Remaining octets must be 0-255.

Usage:
- `nodeconfig.py` uses it for O2CB node IP addresses.

Notable details:
- Python 2 indentation uses tabs/spaces mixed but is consistent enough for the original interpreter.
- Uses old exception syntax and `string.strip`.
