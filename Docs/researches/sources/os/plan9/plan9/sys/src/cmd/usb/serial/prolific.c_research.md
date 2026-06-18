# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/prolific.c

Prolific PL2303-compatible backend for the generic USB serial driver.

Main behavior:
- Provides `plinfo[]` device table and `plmatch`.
- Implements vendor read/write helpers.
- `plinit` determines chip type from release ID or heuristics, performs the Prolific vendor initialization sequence, sets DCR registers, reads line parameters, and starts interrupt status reader.
- `plgetparam` and `plsetparam` map Plan 9 serial parameters to PL2303 line coding bytes.
- `plmodemctl`, `plsendlines`, and `setctlline` manage modem/flow control lines.
- `plsetbreak` sends break control request.
- `plclearpipes` uses vendor pipe reset for HX devices or standard endpoint unstall for others.
- `plreadstatus` reads interrupt endpoint status and updates DCD/DSR/CTS/ring/error counters.
- `statusreader` loops on interrupt status until failure.
- `plseteps` sets bulk endpoint max packet sizes to 256.

Notes:
- The code includes comments comparing behavior to Linux PL2303 handling.
- Some status field assignment looks rough, for example break-error and CTS bits share nearby handling.
