# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevos2p.c

OS/2 Presentation Manager printer device.

- Defines `os2prn`, a printer device intended for Ghostscript as a DLL loaded by a PM application, not text-mode Ghostscript.
- Device state includes OS/2 anchor block, printer DC, presentation spaces, queue name/list, clipping box, and memory DC/PS.
- `os2prn_open` verifies PM process type, discovers printer queues, selects queue from `OS2QUEUE` or filename/default queue, opens a queued printer DC, reads printer resolution and hardcopy caps, sets Ghostscript margins/clipbox, chooses bpp, creates memory DC/PS, starts a print document, and opens a scratch printer file for Ghostscript’s printer framework.
- `os2prn_close` ends the document, destroys presentation spaces/DCs, closes the printer device, and unlinks the scratch file.
- `os2prn_get_params` and `os2prn_put_params` expose `OS2QUEUE` and pre-open `BitsPerPixel`.
- `os2prn_print_page` builds OS/2 `BITMAPINFOHEADER2`/palette data, slices the page into chunks bounded by 64K-ish memory limits, copies Ghostscript scan lines into a DIB buffer, draws bits into a memory bitmap, then bit-blits clipped slices to the printer PS.
- Color mapping supports 24-bit RGB packed as OS/2-expected byte order and black/white fallback; `os2prn_set_bpp` installs color-info and proc table changes while preserving anti-alias data.
- Queue helpers enumerate and free OS/2 print queues via `SplEnumQueue`.
- Risk notes: several OS/2 resource acquisition failures return without unwinding earlier resources; this is legacy platform code with device-context lifetime and clipping correctness as the main maintenance hazards.
