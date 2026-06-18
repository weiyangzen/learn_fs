# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsunr.c

Implements the Ghostscript `sunhmono` printer device, a narrow Sun raster output driver for Harlequin-style 1-bit `SUN_RAS` files.

Key behavior:
- Defines the Sun raster file header fields, magic value, standard/raw raster type, and no-colormap map type used by this driver.
- Registers `gs_sunhmono_device` as a 1-bit printer device at the configured/default 72 DPI with zero margins.
- `sunhmono_print_page` computes Ghostscript scan-line bytes, pads output scan lines to an even byte count, and writes a header followed by all image rows.
- Uses `gdev_prn_get_bits` to fetch each raster row, writes the Ghostscript row bytes, writes a zero pad byte for odd-width rows, then appends the unusual `};\n` terminator expected by the target format variant.
- Allocates one row buffer with Ghostscript memory APIs and returns `VMerror` if allocation fails.

Dependencies:
- Depends on `gdevprn.h`, printer-device macros, `gdev_mem_bytes_per_scan_line`, `gdev_prn_get_bits`, and Ghostscript allocation/error helpers.

Research notes:
- The file explicitly supports only the Harlequin 1-bit no-colormap variant, not the broader Sun raster family.
- Header output is a direct struct write, so portability depends on the build environment matching the expected integer layout/byte order for this Ghostscript port.
