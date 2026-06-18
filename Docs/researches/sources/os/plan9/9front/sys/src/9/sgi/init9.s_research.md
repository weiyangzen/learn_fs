# File Research: sources/os/plan9/9front/sys/src/9/sgi/init9.s

Tiny MIPS assembly entry wrapper for boot startup. `_main` sets the static base register, stores the `boot` function and an argument-frame pointer on the stack, and jumps to `startboot`.

This is a boot-loader-side handoff helper rather than the main kernel entry path.
