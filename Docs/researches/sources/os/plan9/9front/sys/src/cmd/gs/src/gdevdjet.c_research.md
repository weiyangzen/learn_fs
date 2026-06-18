# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdjet.c

Ghostscript HP DeskJet/LaserJet monochrome PCL device definitions and printer-specific wrappers around the generic mono PCL raster pipeline in `gdevdljm.c`.

Key behavior:
- Defines devices for `deskjet`, `djet500`, `fs600`, `laserjet`, `ljetplus`, `ljet2p`, `ljet3`, `ljet3d`, `ljet4`, `ljet4d`, `lp2563`, and `oce9050`.
- `hpjet_open` chooses paper-size-specific margins, handles DeskJet vs LaserJet origin movement, and enables duplex defaults for duplex device variants.
- `hpjet_close` emits duplex odd-page handling and printer reset when pages were printed.
- `hpjet_make_init` augments printer initialization strings with manual-feed or media-source tray selection.
- Per-device `*_print_page_copies` functions choose resolution, PCL initialization commands, and feature masks before calling `dljet_mono_print_page_copies`.
- `oce9050_print_page_copies` enters HPGL/2/RTL mode before printing and advances/resets the plotter afterward.
- `hpjet_get_params` and `hpjet_put_params` expose `ManualFeed` and `%MediaSource` in addition to normal printer parameters.

Notable dependencies:
- Ghostscript printer API: `gdevprn.h`.
- Generic mono PCL feature definitions and print routine from `gdevdljm.h`.

Research notes:
- The file contains many model-specific PCL command strings and margins, reflecting practical printer compatibility rather than a uniform PCL abstraction.
- Fixed-size init buffers are sized for local strings; future longer command strings would need care.
- Media source support maps a small `%MediaSource` range through a two-entry table and ignores null `%MediaSource`.
