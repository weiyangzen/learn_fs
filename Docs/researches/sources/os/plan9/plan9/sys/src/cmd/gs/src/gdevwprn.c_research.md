# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevwprn.c

Older Ghostscript Windows 3.x printer driver `mswinprn`. The file notes it is very slow and, as of 2002-09-14, does not work.

Key responsibilities:
- Defines `gx_device_win_prn`, extending Windows common device state with printer/metafile HDCs, scratch metafile name, palette, pens, brushes, and a small mono staging bitmap.
- `win_prn_open` prompts with `PrintDlg`, creates a printer DC, starts a document, creates a scratch metafile, derives margins/resolution/page size, chooses 1/4/8-bit color behavior, creates palette/tools, and initializes a mono bitmap DC.
- `win_prn_output_page` closes the metafile, replays it into printer bands using `NEXTBAND`, then creates a new metafile for the next page.
- Drawing procs implement fill rectangles, tile rectangles, mono bitmap copies, color bitmap copies, and lines with Windows GDI operations.
- `win_prn_maketools` / `win_prn_destroytools` manage per-color pens and brushes.
- `AbortProc` polls Ghostscript interrupts and cancels on out-of-disk spooler status.

Notable implementation details:
- Rendering is recorded to a Windows metafile (`CreateMetaFile`) rather than sending full page bitmaps.
- Mono tile/copy paths optimize small bitmaps through a cached 32x32-ish staging bitmap.
- Color copy is pixel-by-pixel for 4/8-bit color via `SetPixel`, explaining the driver’s poor performance.

Filesystem relevance:
- Uses a scratch metafile path and unlinks it after creating/playing the metafile. No filesystem architecture logic.
