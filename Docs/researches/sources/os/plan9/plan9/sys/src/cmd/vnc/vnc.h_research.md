# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/vnc.h

This shared VNC header defines the protocol-facing data model used by both the VNC viewer and server. It includes Plan 9 base, bio, draw, and memdraw headers and declares `Pixfmt`, `Colorfmt`, and `Vnc`.

Key definitions:
- `Colorfmt` stores channel maximum and shift.
- `Pixfmt` stores bpp, depth, endian/truecolor flags, and red/green/blue channel formats.
- `Vnc` embeds a `QLock`, network control/data fds, buffered input/output, framebuffer dimensions, pixel format, and client-side desktop name.
- `Color` is an `ulong` used as a byte container in little-endian order.

The enum block maps RFB/VNC wire constants:
- Authentication negotiation: `AFailed`, `ANoAuth`, `AVncAuth`.
- VNC auth results and challenge length.
- Server-to-client messages such as `MFrameUpdate`, `MSetCmap`, `MBell`, `MSCut`.
- Client-to-server messages such as `MPixFmt`, `MSetEnc`, `MFrameReq`, `MKey`, `MMouse`, `MCCut`.
- Encodings: raw, copyrect, RRE, CoRRE, hextile, zlib/tight variants, and mouse warp.
- Hextile tile flags.

It declares the protocol/auth I/O API implemented elsewhere:
- Handshake/auth: `vncauth`, `vnchandshake`, `vncsrvauth`, `vncsrvhandshake`.
- Readers/writers for VNC wire primitives, strings, rectangles, points, and pixel formats.
- Buffered output lifecycle: `vncflush`, `vncterm`, `vncinit`.
- Lock helpers for serialized writes: `vnclock`, `vncunlock`.
- `vnchungup` is deliberately implemented by clients of the I/O library, so server/viewer define their own failure policy.

Notable dependency role:
- This file is the protocol contract for `vncs.c`, `vncv.c`, `wsys.c`, and likely the omitted `auth.c`, `proto.c`, `draw.c`, `color.c`, `rre.c`, and `rlist.c`.
