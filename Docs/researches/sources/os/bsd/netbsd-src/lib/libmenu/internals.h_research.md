# File Research: sources/os/bsd/netbsd-src/lib/libmenu/internals.h

Internal libmenu header declaring private helpers and pattern-match direction constants. It includes `<menu.h>`, defines `MATCH_FORWARD`, `MATCH_REVERSE`, `MATCH_NEXT_FORWARD`, `MATCH_NEXT_REVERSE`, and a local `max(a,b)` macro.

Declared private APIs include item drawing, menu drawing, item navigation, pattern matching, item-size calculation, and item stitching.

This header is internal to libmenu and exposes implementation-level functions not intended as public menu ABI.
