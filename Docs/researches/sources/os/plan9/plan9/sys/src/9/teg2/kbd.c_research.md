# File Research: sources/os/plan9/plan9/sys/src/9/teg2/kbd.c

Reduced PS/2-style scan-code translator used for simulated or external keyboard input on systems without a native keyboard.

Key behavior:
- Maps scan codes through normal, shift, escaped, AltGr, and control tables.
- Tracks modifier state, compose/Latin sequences, caps/num state, and mouse-button pseudo keys.
- Sends translated runes to `kbdq` via `kbdputc`.
- Exposes runtime keymap mutation and enumeration through `kbdputmap` and `kbdgetmap`.

Important functions:
- `kbdputsc(int c, int external)`: central scan-code state machine.
- `kbdenable()`: initializes internal scan state.
- `kbdputmap`, `kbdgetmap`: map editing APIs.

Notes:
- Contains a VM focus workaround: control-alt does not start a compose sequence.
- `F11`/`F12` toggle keyboard debug output.
