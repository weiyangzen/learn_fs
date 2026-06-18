# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idisp.h

Declares display callback installation support.

Key points:
- Forward-declares `display_callback`.
- Declares `display_set_callback(gs_main_instance *, display_callback *)`.

Research notes:
- Called from main interpreter setup to push API display callbacks into the display device.
