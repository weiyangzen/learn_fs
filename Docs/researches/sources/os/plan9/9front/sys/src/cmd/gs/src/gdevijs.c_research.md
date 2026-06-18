# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevijs.c

## Role
`gdevijs.c` implements Ghostscript's `ijs` device, an IPC bridge to an external IJS-compliant inkjet server such as hpijs or gimp-print.

## Device State
- `gx_device_ijs` extends the printer device with:
  - `IjsUseOutputFD`.
  - `IjsServer` executable path/name.
  - color model string and bits per sample.
  - optional manufacturer/model strings.
  - `IjsParams` string.
  - `IjsTumble` state.
  - `IjsClientCtx *ctx` and server protocol version.
- Default device is RGB, 24-bit, 74 DPI sentinel resolution, no print-page proc because output is handled by `gsijs_output_page`.

## Open and IPC Behavior
- `gsijs_open` requires `IjsServer`; if `IjsUseOutputFD` is true it opens Ghostscript printer output and passes a duplicated FD to the server as `OutputFD`, otherwise it leaves output file creation to the server through `OutputFile`.
- Starts the external server with `ijs_invoke_server`, opens the IJS connection, begins job 0, sends output target, manufacturer/model, generic params, negotiated resolution, and margins.
- `gsijs_close` ends the job, closes the IJS connection, sends an exit command, closes the printer device, and frees allocated strings.

## Parameter Handling
- `gsijs_get_params` exposes `IjsServer`, `DeviceManufacturer`, `DeviceModel`, `IjsParams`, `BitsPerSample`, `IjsUseOutputFD`, and `Tumble`.
- `gsijs_put_params` enforces closed-device-only constraints for server, model/manufacturer, params, bits, output-FD mode, and process color model. `Tumble` can change more freely.
- `gsijs_read_string` uses `dev->LockSafetyParams` to reject `IjsServer` changes when safety params are locked.
- `gsijs_set_color_format` supports `DeviceGray`, `DeviceRGB`, and `DeviceCMYK`; it sets Ghostscript color procs, component counts, polarity, depth, and linear-color masks.

## Page Output
- `gsijs_output_page` calculates raster width/height, sends required IJS page params (`NumChan`, `BitsPerSample`, `ColorSpace`, `Width`, `Height`, `Dpi`), then for each copy begins an IJS page, sends each scanline via `ijs_client_send_data_wait`, ends the page, finalizes clist page output if needed, and calls `gx_finish_output_page`.
- For old hpijs version 0.29, white rows may be sent as zero-length data.

## Margin and Resolution Negotiation
- Has special hpijs 1.0/1.0.2 code paths keyed by `HPIJS_1_0_VERSION`.
- Parses `WxH` values with `gsijs_parse_wxh`.
- Queries server `Dpi`, `PrintableArea`, and `PrintableTopLeft` where available; adjusts Ghostscript margins and can reallocate printer memory after changing resolution.

## Risks and Notes
- Security-sensitive: comments warn that `IjsServer` can be selected on the Ghostscript command line and recommend `-dSAFER` / locked safety params. This file starts an external program and may pass file paths or file descriptors to it.
- There is a small string bug in `gsijs_read_string`: after `strncpy`, it writes `str[new_value.size+1] = '\0'` rather than `str[new_value.size] = '\0'`.
- This is the main process and output-file boundary in the group.
