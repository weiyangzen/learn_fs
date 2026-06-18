# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsvga.c

Implements legacy DOS SuperVGA display devices for Ghostscript, including shared 256-color frame-buffer operations and chipset-specific mode/page switching.

Key behavior:
- Maintains an 8-bit palette model with a fixed 64-entry color cube plus dynamically assigned DAC entries from index 64 upward unless the device uses fixed colors.
- `svga_find_mode` selects the smallest mode table entry that satisfies the requested width/height, adjusts device resolution, and records the frame-buffer raster.
- `svga_open` saves the prior display mode, switches to the selected graphics mode, initializes DAC colors, and resets the current 64K page window; `svga_close` restores the saved mode.
- `svga_map_rgb_color` maps RGB to fixed PC palette entries or dynamically hashes 5-bit RGB values into assignable DAC entries; it returns `gx_no_color_index` if the dynamic table is exhausted.
- `svga_fill_rectangle`, `svga_copy_mono`, `svga_copy_color`, `svga_get_bits`, and `svga_copy_alpha` draw directly into banked video memory at segment `0xa000`, changing pages as offsets cross 64K windows.
- `svga_copy_alpha` approximates alpha as saturation toward white and lazily allocates palette shades for intermediate alpha levels.
- Defines a VESA device that queries BIOS mode info, validates bank-window geometry, supports one or two read/write windows, and uses either a BIOS page function pointer or interrupt `0x10` bank switching.
- Defines ATI Wonder, Trident, Tseng ET3000/ET4000, Cirrus CL-GD54XX, and Avance Logic devices with chipset-specific mode tables and page-select register programming.

Dependencies:
- Uses Ghostscript device/color/parameter APIs from `gxdevice.h`, `gdevpccm.h`, `gdevpcfb.h`, and `gdevsvga.h`.
- Uses DOS-era BIOS/register, segment pointer, I/O port, interrupt, and optional assembly helpers such as `int86`, `int86x`, `outportb`, `inportb`, `MK_PTR`, `disable`, and `enable`.

Research notes:
- This is hardware-facing display code, not a Plan 9 OS subsystem despite its location in the vendored Plan 9 Ghostscript tree.
- Correctness is tightly coupled to banked VGA assumptions: 64K windows, byte-per-pixel 8-bit modes, and chipset register semantics.
- The shared dynamic color table is file-global, so multiple open SVGA devices would not have independent dynamic palette state.
