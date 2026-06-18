# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/vmxgdb.c

## Role

`vmxgdb.c` is a small GDB remote serial protocol bridge for an already-mounted `vmx` instance. It reads GDB packets from standard input/output and answers a minimal set of register and memory queries by reading `/n/vmx/xregs` and `/n/vmx/mem`.

## Protocol Behavior

- `rpack()` waits for `$...#csum` packets, handles escaped bytes, validates checksums unless no-ack mode is active, and sends `+` or `-` acknowledgements.
- `wpack()` emits escaped response packets and retransmits on `-` unless no-ack mode is active.
- Supports `qSupported` with `PacketSize=4096;QStartNoAckMode+`.
- Supports `QStartNoAckMode`.
- Supports `?` with a fixed `S00`.
- Supports `g` by returning the x86 register packet.
- Supports `mADDR,LEN` memory reads, capped at 65536 bytes.
- Treats `H` thread-selection packets by reinterpreting the second byte as a simple packet.

## Register And Memory Mapping

- `regpacket()` maps GDB i386-style register order to `ax`, `cx`, `dx`, `bx`, `sp`, `bp`, `si`, `di`, `pc`, `flags`, `cs`, `ss`, `ds`, `es`, `fs`, and `gs`.
- Segment register values are forced to zero in the emitted packet.
- `memread()` parses hexadecimal address/count pairs, clears the sign bit to avoid negative Plan 9 file offsets, reads from `memfd`, and hex-encodes bytes.

## Notable Limitations And Risk Areas

- The implementation is read-only: no register writes, memory writes, continue, step, breakpoints, or thread model.
- It assumes `vmxroot` is `/n/vmx`.
- `memread()` reverses through the read buffer when hex-encoding in place; this relies on the destination allocation being twice the requested count.
- Unsupported packets get an empty response, which is acceptable for many GDB feature probes but limited for active debugging.
