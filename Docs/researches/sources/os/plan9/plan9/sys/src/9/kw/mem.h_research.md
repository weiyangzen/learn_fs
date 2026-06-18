# File Research: sources/os/plan9/plan9/sys/src/9/kw/mem.h

## Role

Kirkwood ARM memory-layout and machine-constant header. It defines page size, kernel segments, user/kernel address bounds, timing constants, cache line size, PTE flags, and physical device addresses.

This is platform memory infrastructure used by MMU, drivers, and storage code.

## Main Contents

- Size units: `KiB`, `MiB`, `GiB`.
- Page and stack constants:
  - `BY2PG`, `PGSHIFT`, `KSTKSIZE`, `STACKALIGN`
- Kernel/user layout:
  - `KSEG0`, `KZERO`, `KTZERO`, `CONFADDR`, `L1`
  - `UZERO`, `UTZERO`, `USTKTOP`, `USTKSIZE`, `TSTKTOP`
- Time/cache constants:
  - `CLOCKFREQ`
  - `CACHELINESZ`
- PTE and color constants:
  - `PTEVALID`, `PTEWRITE`, `PTEKERNEL`, `PTEMAPMEM`
- Physical addresses:
  - `PHYSDRAM`
  - `PHYSIO`
  - `PHYSCONS`
  - `PHYSNAND1`
  - `PHYSNAND2`
  - `PHYSSPIFLASH`
  - `PHYSBOOTROM`
- `VIRTIO` maps IO virtually at the same base as physical IO.

## Important Behavior

- Establishes the kernel virtual segment at `0x60000000`.
- Uses a 4 KiB page size.
- Sets the Kirkwood TCLK clock frequency to 200 MHz.
- Defines direct physical constants consumed by NAND, UART, SDIO, USB, and MMU code.

## Dependencies And Assumptions

- Assumes single-machine build (`MAXMACH 1`).
- Assumes kernel physical/virtual mapping conventions used by `l.s` and `mmu.c`.

## Notable Risks

- Constants are global architectural contracts; changing one requires auditing assembly and C code.
