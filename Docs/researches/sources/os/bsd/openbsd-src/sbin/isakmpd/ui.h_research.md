# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ui.h

`ui.h` declares the FIFO control interface constants and public entry points. It defines `FIFO` as `/var/run/isakmpd.fifo` and `RESULT_FILE` as `/var/run/isakmpd.result`.

The header exports `ui_fifo`, `ui_socket`, `ui_daemon_passive`, `ui_init()`, `ui_handler()`, and `ui_report()`. It is small but exposes daemon-wide control state.
