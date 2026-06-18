# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/proto.c

## Role

`proto.c` implements shared RFB/VNC binary protocol read/write primitives over Plan 9 buffered I/O.

## Main Behavior

- `vncinit()` initializes `Biobuf` readers/writers and stores network/control fds in `Vnc`.
- `vncterm()` closes buffered streams.
- Provides big-endian readers/writers for bytes, shorts, longs, points, rectangles, compact rectangles, pixel formats, and strings.
- `vncrdstringx()` bypasses `Biobuf` for server-side negotiation cases where later protocol wrappers need direct fd access with no buffered data.
- `vncflush()`, `vncrdbytes()`, and `vncwrbytes()` detect I/O failure and call `vnchungup()`.
- `vnclock()` and `vncunlock()` serialize writes through the embedded `QLock`.
- `vncgobble()` discards a fixed number of incoming bytes.

## Notable Limitations And Risk Areas

- Most read/write failures are converted into `vnchungup()` rather than returned as errors.
- `vncrdstring()` allocates `len+1` without a local maximum; callers trust protocol sizes.
- `vncrdstringx()` asserts no buffered input before direct reads.
