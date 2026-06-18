# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmeds.c

Implements shared media selection support for printer drivers.

Key behavior:
- Defines a static table of known media sizes in meters, including ISO A/B series, architectural sizes, US paper sizes, and envelopes.
- Each media table entry includes a priority of `1 / (width * height)`, so smaller matching media have higher priority.
- `select_medium(gx_device_printer *pdev, const char **available, int default_index)`:
  - Converts current device width and height from pixels/dpi to meters.
  - Iterates through the caller-provided null-terminated media-name list.
  - Finds matching known media whose width and height exceed the image dimensions plus a 0.1 cm tolerance.
  - Chooses the smallest suitable available medium by priority.
  - Falls back to `default_index` if no medium matches.

Dependencies and notes:
- Included by printer drivers such as `gdevl31s.c`.
- The function is orientation-sensitive: it compares width-to-width and height-to-height without trying rotated media.
