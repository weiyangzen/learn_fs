# File Research: sources/os/plan9/9front/sys/src/9/omap/init9.s

Tiny assembly `main` for boot startup.

Key behavior:
- Sets the static base register R12.
- Passes `boot` and an argv pointer to `startboot`.
- Loops forever if `startboot` returns.

Research notes:
- The comment explains this is assembly to avoid dragging in extra C runtime routines before SB is initialized.
