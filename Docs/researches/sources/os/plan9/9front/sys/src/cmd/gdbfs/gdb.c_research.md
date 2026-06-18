# File Research: sources/os/plan9/9front/sys/src/cmd/gdbfs/gdb.c

## Purpose
Implements a client for the GDB remote serial protocol behind `gdbfs` 9P operations.

## Key Elements
Maps GDB register packets to Plan 9 `Ureg` layouts for ARM and AMD64, converts hex payloads, formats checksum packets, runs a dedicated packet I/O proc, negotiates `qSupported` packet size, handles memory read/write, register read, continue, stop, start-stop, wait-stop, detach/shutdown, checksums, acks, and target stopped/running state.

## Dependencies
Uses Plan 9 thread channels, Bio, 9P request helpers, libmach register metadata, and GDB remote commands `g`, `m`, `M`, `c`, `?`, `D`, and `qSupported`.

## Behavior/Risks
Register write is unimplemented. Packet I/O is mostly serialized, but interrupt writes are deliberately sent outside the main packet lock. Memory operations require target state `Stopped`. Unsupported machine register maps fail at runtime.
