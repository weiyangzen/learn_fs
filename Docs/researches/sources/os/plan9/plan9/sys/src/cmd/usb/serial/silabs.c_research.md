# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/silabs.c

Silicon Labs CP210x-style backend for the generic USB serial driver.

Main behavior:
- Matches CP210x VID/DID pairs in `slinfo[]`.
- Provides vendor request helpers `slread`, `slwrite`, and `slput`.
- `slinit` enables UART operation and reads initial parameters.
- `slgetparam` reads baud and line control register, decoding bits/parity/stop.
- `slsetparam` writes line control and baud.
- `seteps` disables read timeout on input endpoint.
- `wait4data` repeatedly reads until nonzero data.

Exports `slops` with init/getparam/setparam/seteps/wait4data hooks.

Style note:
- `slmatch` uses legacy K&R implicit-int style.
