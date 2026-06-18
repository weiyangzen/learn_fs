# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/fns.h

`fns.h` declares the emulator subsystem interfaces: operand constructors/read/write, decoder, executor/trap/interrupt entry points, formatters, PIT operations, and PCI config access helpers.

It also defines `BDFBNO`, `BDFDNO`, and `BDFFNO` macros for extracting bus/device/function fields from a PCI BDF value.
