# File Research: sources/os/bsd/dragonflybsd/sys/sys/cons.h

Kernel console driver registration and console-device operation interface.

Key responsibilities:
- Defines console callback typedefs for probe, init, init-fini, term, get/check/put char, debugger control, and polling.
- Defines `struct consdev`, including callback vector, associated tty/cdev, priority, probe status, private pointers, unit, and flags.
- Defines console availability/debug support flags and console selection priorities.
- Provides `CONS_DRIVER` macro to register console devices in `cons_set`.
- Declares kernel console entry points: `cncheckc`, `cngetc`, `cninit`, `cninit_finish`, `cndbctl`, `cnputc`, and `cnpoll`.

Dependencies:
- Includes `sys/types.h`; kernel users rely on data-set registration macros and tty/cdev definitions elsewhere.

Notable risks:
- Console selection depends on probe routines setting `cn_probegood` and priority consistently.
- Console callbacks can be used in early boot/debug contexts, so implementations must tolerate limited kernel services.
