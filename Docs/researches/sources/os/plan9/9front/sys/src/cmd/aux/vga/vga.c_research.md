# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vga.c

Implements generic VGA register access and generic VGA mode programming.

Key responsibilities:
- Provides byte/indexed register helpers: `vgai`, `vgaxi`, `vgao`, `vgaxo`.
- Handles VGA attribute controller access sequencing through `Status1`.
- Snarfs baseline VGA state: misc, feature, sequencer, CRT, graphics, attribute, and optionally palette.
- Initializes generic VGA register state from a `Mode`, including sync polarity, sequencer setup, CRT timing, overflow bits, pitch, graphics controller, attribute controller, and palette.
- Loads generic VGA register state back to hardware.
- Dumps register sets and shared VGA timing/clock/memory metadata.

Important interfaces:
- Exports `Ctlr generic`.
- Uses constants and structures from `vga.h`.
- Calls `palette` controller methods when `dflag` is set.

Notes:
- CRT setup handles vertical interlace by halving vertical timing fields.
- The pitch calculation uses `vga->virtx`, matching comments in `vga.h` about virtual width correctness.
