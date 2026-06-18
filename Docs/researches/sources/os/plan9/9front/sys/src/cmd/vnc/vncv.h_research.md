# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/vncv.h

## Role

`vncv.h` declares viewer-side globals and cross-module functions.

## Contents

- Color conversion: `choosecolor()`, `cvtpixels`, `settranslation()`.
- Update handling: `sendencodings()`, `requestupdate()`, `readfromserver()`.
- Shared globals: `zero`, `charset`, `encodings`, `autoscale`, `bpp12`, `vnc`, and `mousefd`.
- Window/input/clipboard hooks: `adjustwin()`, `readkbd()`, `initmouse()`, `mousewarp()`, `readmouse()`, `senddim()`, `writesnarf()`, and `checksnarf()`.

## Notable Limitations And Risk Areas

- Some declarations, such as `settranslation()` and `senddim()`, are not implemented in the files in this group, suggesting compatibility leftovers or external/conditional definitions.
- The header exposes process-global viewer state used across rforked processes.
