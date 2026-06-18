# File Research: sources/os/plan9/9front/sys/src/9/mt7688/init9.s

This short MIPS assembly file is the user init bootstrap stub. `_main` sets `R30` to `setR30(SB)`, passes the string `boot` and a frame pointer-derived argument pointer on the stack, then jumps to `startboot(SB)`.

It is part of the transition from the kernel-created initial user process to `/boot`. It does not implement filesystem logic, but it is the first user-mode code path that ultimately opens the root and boot namespace.

The file is intentionally tiny and depends on the Plan 9/MIPS calling convention and the `boot` symbol being provided elsewhere in the init code build.
