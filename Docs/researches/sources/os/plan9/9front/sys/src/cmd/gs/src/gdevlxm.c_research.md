# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlxm.c

Implements the `lxm5700m` Lexmark 5700 monochrome inkjet printer driver.

Key behavior:
- Defines `lxm_device`, a `gx_device_printer` subclass carrying `headSeparation`.
- Registers `gs_lxm5700m_device` at 600x600 dpi with default `HeadSeparation = 16`.
- Exposes `HeadSeparation` through `lxm_get_params` and validates it in `lxm_put_params` as 1 through 32.
- Emits printer initialization macros `init1`, `init2`, and `init3`.
- Prints in overlapping 208-pixel-high swipes with `overLap = 104`.
- Skips blank regions but backs up by the overlap distance so later swipes can reinforce earlier dots.
- Computes left/right byte bounds for each swipe.
- Encodes each output column using a 13-word directory that identifies which 16-bit vertical sectors have data.
- Alternates `RIGHTWARD` and `LEFTWARD` direction, changing how even/odd columns map to the two printhead columns and `headSeparation`.
- Dynamically grows `swipeBuf` if the compressed swipe exceeds the current allocation.
- Writes swipe headers containing vertical delta, byte size, horizontal extent, and encoded column data, then ejects with `fin()`.

Dependencies and notes:
- Uses `gsparams.h` for parameter handling.
- The driver is intentionally monochrome and cartridge-calibration-oriented.
- The buffer-growth macro jumps to an allocation cleanup label on failure.
