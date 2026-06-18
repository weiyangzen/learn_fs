# File Research: sources/os/plan9/plan9/sys/src/9/kw/dat.h

## Purpose
Defines core machine-dependent kernel types and globals for the Plan 9 Kirkwood ARM port.

## Key Definitions
- Forward declarations for core kernel structures such as `Conf`, `FPsave`, `Label`, `Lock`, `Mach`, `Proc`, `Page`, `Soc`, and `Ureg`.
- `Lock`: spin lock state including key, saved status register, PC, owning proc/mach, and interrupt-lock flag.
- `Label`: saved stack and PC for scheduler context.
- `FPsave`: emulated floating-point save area and FP state flags.
- `Conf` / `Confmem`: boot-time memory and sizing configuration.
- `MMMU` and `PMMU`: machine/proc MMU state, including L1 table tracking and cached L2 page list.
- `Mach`: per-CPU state including current proc, scheduler label, alarms, ticks, CPU/SOC IDs, fast clock, stats, exception save stacks, and performance state.
- `ISAConf` and `DevConf`: parsed device configuration descriptors.
- `Memcache`: cache geometry summary.
- `Soc`: global memory-mapped SoC register base addresses.

## Globals and Constants
- Declares register globals `m` and `up`.
- Declares `kseg0`, `machaddr`, `memsize`, debug flags, and `soc`.
- Defines `Frequency = 1200 MHz`, one cache color, vector page layout, fake `kmap`, and `active` machine state.

## Dependencies and Integration
Included broadly by kernel C files in this port. It bridges architecture-specific structures to common `portdat.h`.

## Risks and Notes
This is foundational ABI/configuration surface for the port. Changes affect scheduler, memory management, interrupt handling, device setup, and process accounting.
