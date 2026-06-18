# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idisp.h

Header for display callback installation. It forward-declares `display_callback` and declares:
- `display_set_callback(gs_main_instance *minst, display_callback *callback)`

Called from the interpreter main path after API callback setup.
