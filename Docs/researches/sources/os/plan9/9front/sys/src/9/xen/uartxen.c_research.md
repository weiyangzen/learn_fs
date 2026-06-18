# File Research: sources/os/plan9/9front/sys/src/9/xen/uartxen.c

Xen console ring as a Plan 9 UART.

Purpose:
- Adapts Xen console shared ring and event channel to Plan 9 UART/console interfaces.

Key behavior:
- Maps console ring at `XENCONSOLE` and records event channel from `start_info`.
- `xenuartputs` and `xenputc` write directly to the console output ring and notify backend.
- `interrupt` consumes input ring bytes and feeds `uartrecv`.
- `kick` drains Plan 9 serial output queue into Xen console ring.
- UART parameter methods accept only supported virtual-console settings.
- `kbdenable` enables console input when `console=0` is configured.

Integration:
- Used by early Xen `main()` for console output and later by Plan 9 UART/keyboard console paths.

Risks/notes:
- Output is dropped when the Xen console ring is full.
- Console settings are mostly nominal; real serial hardware controls are no-ops.
