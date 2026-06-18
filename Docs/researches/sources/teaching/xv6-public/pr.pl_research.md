# File Research: sources/teaching/xv6-public/pr.pl

Perl formatter used by the xv6 print/PDF pipeline.

Behavior:
- Prints input in 50-line pages with date, heading, page number, and optional sheet labels.
- Supports `-h` heading override.
- Strips `//DOC` annotations from emitted lines.
- Pads each page to fixed height.

Used by `runoff` when producing printable source listings.
