# File Research: sources/os/bsd/netbsd-src/lib/libcurses/keypad.c

Implements keypad mode control: `keypad` and `is_keypad`.

`keypad` toggles `__KEYPAD` on the target window and emits the terminal `keypad_xmit` capability the first time any active screen enters keypad transmit mode. It clears only the window flag when disabling. `is_keypad` reports the flag state.
