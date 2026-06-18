# File Research: sources/os/plan9/9front/sys/src/9/pc/devkbd.c

PS/2 i8042 keyboard and auxiliary-port device implementing raw scancode access.

Key responsibilities:
- Initializes the 8042 controller, enables scan-code set 1 keyboard interrupts, disables auxiliary interrupts by default, and allocates I/O ports.
- Provides `#b/scancode` for exclusive raw scancode reads and `#b/leds` for lock LED writes.
- Handles keyboard and auxiliary interrupts, routing mouse bytes to an installed aux callback.
- Implements i8042 reset command sequence used by architecture reset.
- Provides `i8042auxenable()` and `i8042auxcmd()` for PS/2 mouse support.
- Shuts down keyboard/aux transfers and interrupts on device shutdown.

Important behavior:
- `#b/scancode` can only be opened by `eve` and only one reader at a time.
- The scancode queue is nonblocking and coalescing.
- `kbdpoll()` opportunistically invokes the interrupt handler if the queue is empty.
- LED updates avoid redundant writes and use keyboard command `0xed`.

Dependencies:
- Depends on PC keyboard controller ports, interrupt registration, queues, device framework, and privilege checks.

Notable risks:
- `i8042reset()` is skipped when no keyboard controller was successfully initialized.
- Aux command failure prints returned byte and caller PC for diagnostics.
