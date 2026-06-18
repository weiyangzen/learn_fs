# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hastd.h

Read completely: 53 lines.

This header exposes shared daemon globals and cross-module entry points for the HAST daemon core.

Key responsibilities:
- Declares global `cfgpath`, `sigexit_received`, and pidfile handle `pfh`.
- Declares descriptor cleanup/assertion helpers used after forking worker processes.
- Declares primary and secondary worker entry points.
- Declares `primary_config_reload()` for parent-to-primary live reload requests.

Important interactions:
- Includes `hast.h` for `struct hast_resource`.
- Includes `<nv.h>` because primary reload messages are NV encoded.
- Shared by `hastd.c`, `primary.c`, and other role/control modules.

Reliability notes:
- This is a small cross-module contract; changes affect process lifecycle, signal shutdown, worker startup, and reload behavior.
