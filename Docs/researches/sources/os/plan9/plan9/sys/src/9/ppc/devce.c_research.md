# File Research: sources/os/plan9/plan9/sys/src/9/ppc/devce.c

## Role

Skeleton Plan 9 device driver for “channel element” DSP-like devices on a Saturn/UCU board.

## Main Data

Defines UCU/DSP state constants, qid types, CPLD register layout, circular buffer and DSP structs, and a global `Ce` containing UCU type and up to 16 DSP/channel entries. CPLD is mapped at `Saturn + 0x6000000`; CE memory at `Saturn + 0x3000000`.

## Control Flow

`ceinit` checks the CPLD UCU version bit and records `Ucu64`, otherwise prints unsupported UCU. The device exposes `#C` with `cectl` and `ce0` through `ce15` entries via `cegen`. Open marks the channel open; read supports directory reads only; writes are a no-op returning 0.

## Dependencies

Uses Plan 9 `Dev` interface, `msaturn.h`, and standard device helpers.

## Risks

This driver is incomplete. Data-file reads and writes report unsupported/no-op behavior, and several qid constructions appear inconsistent (`QID(Qce, i)` uses type/device fields in a surprising order). It is mainly scaffolding.
