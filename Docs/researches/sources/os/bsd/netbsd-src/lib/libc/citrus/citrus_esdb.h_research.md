# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_esdb.h

Data structures and API for loaded Encoding Scheme Database records.

Key contents:
- `_citrus_esdb_charset` holds a charset id and charset name.
- `_citrus_esdb` holds encoding name, optional variable payload, charset count/list, and optional invalid wide character.
- Declares alias, open, close, list-free, and list-enumeration functions.

Used by encoding/conversion setup code to map names to module/charset metadata.
