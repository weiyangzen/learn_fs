# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsparams.h

Declares parameter-list serialization APIs.

Key behavior:
- Includes `stream.h` and `gsparam.h`.
- Contains a disabled future stream interface (`gs_param_list_puts`, `gs_param_list_gets`) implemented in `gsparam2.c`.
- Exposes the active buffer interface:
  - `gs_param_list_serialize`
  - `gs_param_list_unserialize`

Integration:
- The active path maps to `gsparams.c`.
- The stream path is present but disabled with `#if 0`.

Risk notes:
- Consumers using the active interface must provide a void-pointer-aligned buffer for unserialization.
- Header comments make clear that success for serialization requires returned size to be positive and not exceed supplied buffer size.
