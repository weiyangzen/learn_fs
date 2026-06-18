# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/charsets.xml

Stores a local copy of the IANA Character Sets registry XML used by the `tcs` build tooling.

Key points:
- XML registry root is `id="character-sets"` with `updated` date `2013-12-20`.
- Describes charset registration rules, MIBenum ranges, alias conventions, and synchronization expectations with the IANA charset MIB.
- Contains 215 `<record>` entries for charset registrations, plus a `<people>` section of registry contacts.
- Contains 653 `<alias>` or `<preferred_alias>` tags and 546 `<xref>` tags.
- Early records cover US-ASCII, ISO-8859 variants, JIS, Shift_JIS, EUC-JP, and many ISO-646 national variants.
- Later records include Unicode/ISO-10646 forms, vendor and Windows/IBM code pages, Mac encodings, GB/KSC/Big5/HZ, UTF-7/8/16/32 variants, BOCU/SCSU, and other registered names.

Dependencies and interactions:
- `mkfile` can fetch this file and uses it with `charsets.awk` and `alias.txt` to generate `alias.h`.
- The XML itself is registry data; it is not parsed by runtime conversion code.

Research relevance:
- Important build-time metadata source for keeping `tcs` charset aliases aligned with IANA names.
