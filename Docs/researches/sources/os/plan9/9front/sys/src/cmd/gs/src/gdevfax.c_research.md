# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevfax.c

## Role
`gdevfax.c` implements fax output devices and shared CCITT fax compression helpers.

## Device Definitions
- Defines `gdev_fax_std_procs`, adding fax-specific parameter get/put over standard printer device procs.
- Defines devices:
  - `gs_faxg3_device`: Group 3 1-D.
  - `gs_faxg32d_device`: Group 3 2-D.
  - `gs_faxg4_device`: Group 4.

## Parameters
- `gdev_fax_get_params` and `gdev_fax_put_params` expose `AdjustWidth`, constrained to 0 or 1.
- `gdev_fax_init_state_adjust` initializes CCITTFaxEncode defaults, sets `Columns`, `Rows`, and `BlackIs1`, and optionally adjusts widths near legal fax widths to A4 1728 or B4 2048 columns.

## Compression Path
- `gdev_fax_print_strip` initializes the selected stream template, allocates input/output buffers, feeds scanlines through the stream encoder, writes output chunks to `prn_stream`, and releases the stream state.
- It pads input when adjusted fax width is wider than the device scanline width.
- Special-cases output filename `nul` by skipping actual writes.
- `gdev_fax_print_page` compresses an entire page as one strip using `s_CFE_template`.
- The three device print functions configure `K`, `EndOfLine`, and `EndOfBlock` for G3/G32D/G4.

## Risks and Notes
- Reusable compression helper likely used by non-fax image formats elsewhere.
- File I/O is sequential output only; no filesystem metadata behavior.
