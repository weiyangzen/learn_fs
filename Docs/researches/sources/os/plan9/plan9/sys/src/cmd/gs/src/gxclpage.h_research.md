# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpage.h

## Purpose
Declares saved-page APIs for command-list printer devices.

## Main Responsibilities
- Documents how clients save a banded page object.
- Documents how clients render multiple saved pages with offsets.
- Declares:
  - `gdev_prn_save_page`
  - `gdev_prn_render_pages`

## Dependencies
- Requires `gdevprn.h` and `gxclist.h`.
- Includes `gxclio.h`.

## Research Notes
The header clarifies ownership: clients provide/free saved and placed page storage, while the rendering routine consumes compatible clist temporary files.
