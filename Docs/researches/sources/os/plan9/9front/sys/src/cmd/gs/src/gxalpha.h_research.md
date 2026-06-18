# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxalpha.h

Documents Ghostscript's internal alpha-channel premultiplication policy.

Key behavior:
- Establishes that alpha compositing uses premultiplication toward the native zero color: black for DeviceGray/DeviceRGB and white for DeviceCMYK.
- Records expected effects on `alphaimage`, `readimage`, color mapping, image operators, and compositing.
- Documents current interpretation that `readimage` returns device-stored premultiplied pixels, `alphaimage` expects premultiplied input, and image/colorimage treat input as opaque.

Research notes:
- The file is mostly policy documentation with one optional compile-time switch, `PREMULTIPLY_TOWARDS_WHITE`, left commented out.
