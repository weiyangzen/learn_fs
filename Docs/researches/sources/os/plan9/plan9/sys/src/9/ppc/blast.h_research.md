# File Research: sources/os/plan9/plan9/sys/src/9/ppc/blast.h

## Role

Board-specific constants for the Crawford Hill Blast PowerPC board.

## Main Definitions

Defines clock input (`CLKIN` 72 MHz), memory/chip-select layout, `IMMR`, flash/DSP/SDRAM/FPGA base and size constants, `PLAN9INI`, TLB entry count, PPC PTE policy bits, SMC UART pins, and FCC Ethernet pin masks/options for multiple ports.

## Dependencies

Consumed by PPC platform initialization, MMU setup, flash, UART, and FCC Ethernet code. It assumes PPC PTE bit definitions and `BIT()` are already available.

## Risks

This is hardware-description data. Incorrect base addresses, sizes, BAT assumptions, or pin masks can cause boot failure or device misconfiguration. `MEM2SIZE` is forced to zero despite a commented 32 MiB value, so local-bus SDRAM is intentionally disabled here.
