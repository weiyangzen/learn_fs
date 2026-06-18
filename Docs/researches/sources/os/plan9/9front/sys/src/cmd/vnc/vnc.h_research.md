# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/vnc.h

## Role

`vnc.h` is the shared public header for the VNC viewer/server protocol code.

## Main Definitions

- `Colorfmt`, `Pixfmt`, and `Vnc`.
- `Vnc` embeds a `QLock`, network/control fds, input/output `Biobuf`s, framebuffer dimensions, pixel format, client-side server metadata, resize capability, and one screen descriptor.
- Defines RFB constants for version length, auth types/statuses, message types, encoding numbers, pseudo-encodings, and hextile flags.
- Defines `Color` as a byte-storage comparison type.
- Declares auth, handshake, protocol read/write, string, rectangle, pixel-format, flush, lock, and hangup functions.

## Notable Limitations And Risk Areas

- The `Vnc` struct is shared by both viewer and server code; some fields are only meaningful on one side.
- Protocol constants include legacy and pseudo-encoding values with signed negative encodings represented as enum constants.
- Callers must hold `vnclock()` for multi-field writes that need to remain contiguous.
