# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/realmode0.s

This assembly file performs the low-level protected-mode to real-mode transition, executes a BIOS interrupt, and returns to protected mode with paging enabled.

Key responsibilities:
- Defines descriptor pointers for physical and virtual GDT/IDT state.
- Saves and restores general registers and flags.
- Switches to low physical code and stack, loads a real-mode IDT, disables paging, enters 16-bit compatibility mode, then clears protected mode.
- Loads BIOS call registers from `RMUADDR`, executes the patched `INT`, saves registers and flags back to `RMUADDR`, then re-enters protected mode.
- Restores kernel segment registers, paging, IDT, GDT, and original stack.
- Includes a Multiboot header placed near the image start.
- Defines a small 16-bit-compatible GDT and pointer.

Filesystem/storage relevance:
- Enables BIOS disk services during bootstrap, which can be the only available storage path before native disk drivers are initialized.
