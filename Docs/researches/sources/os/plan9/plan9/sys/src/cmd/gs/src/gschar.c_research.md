# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gschar.c

Implements Ghostscript client-facing character/show operator wrappers.

Key contents:
- Includes Ghostscript graphics state, device, memory-device, character, and font internals.
- Provides `gs_show_enum_release`.
- Implements initialization wrappers for PostScript text operators:
  - `gs_show_n_init`
  - `gs_ashow_n_init`
  - `gs_widthshow_n_init`
  - `gs_awidthshow_n_init`
  - `gs_kshow_n_init`
  - `gs_xyshow_n_init`
  - `gs_glyphshow_init`
  - `gs_glyphpath_init`
  - `gs_glyphwidth_init`
  - `gs_cshow_n_init`
  - `gs_stringwidth_n_init`
  - `gs_charpath_n_init`
  - `gs_charboxpath_n_init`
- Implements cache/metrics wrappers:
  - `gs_setcachedevice_float`
  - `gs_setcachedevice_double`
  - `gs_setcachedevice2_float`
  - `gs_setcachedevice2_double`
  - `gs_setcharwidth`
- Implements enumeration/accessor functions:
  - `gs_show_next`
  - `gs_show_width_only`
  - `gs_show_current_char`
  - `gs_show_current_glyph`
  - `gs_show_current_width`
  - `gs_kshow_previous_char`
  - `gs_kshow_next_char`
  - `gs_show_width`
- Internal helper `show_n_begin` normalizes the text enumerator implementation to `gs_show_enum`.

Behavior:
- Most init functions call a lower-level `gs_*_begin` text routine and then pass through `show_n_begin`.
- `gs_kshow_n_init` rejects composite and CID font types as invalid for `kshow`.
- Float cache-device APIs convert to double arrays for backward compatibility.
- Cache-device and setcharwidth APIs validate that the enumerator belongs to the passed graphics state.

Important implementation notes:
- This file is an adapter layer around the newer `gs_text_*` machinery.
- `show_n_begin` falls back to default device text handling if the device produced a different text enumerator type, temporarily replacing the device `text_begin` proc.
- `gs_kshow_next_char` directly indexes `penum->text.data.bytes[penum->index]`, so it assumes byte-string text data for that path.
