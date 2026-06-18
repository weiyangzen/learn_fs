# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/vncv.h

This viewer-side header declares cross-file VNC viewer helpers.

Color/display declarations:
- `choosecolor`, `settranslation`, and `cvtpixels` choose/perform framebuffer pixel conversion.
- `zero[]` is an external byte buffer used by drawing code.

Server protocol/draw declarations:
- `sendencodings` sends the viewer's preferred encoding list.
- `requestupdate` asks the server for framebuffer changes.
- `readfromserver` consumes server messages and paints the local draw window.

Viewer globals:
- `encodings`, `bpp12`, `vnc`, and `mousefd` are defined by `vncv.c`.

Window-system/input declarations:
- `readkbd`, `initmouse`, `mousewarp`, `readmouse`, `senddim`, `writesnarf`, and `checksnarf`.

Role:
- This is the shared contract among `vncv.c`, `wsys.c`, and omitted viewer draw/color modules.
