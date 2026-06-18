# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxalpha.h

Purpose: Documents and centralizes Ghostscript internal alpha-channel premultiplication policy.

Contents:
- Explains Porter-Duff-style premultiplication for alpha.
- States Ghostscript’s chosen convention: premultiply toward the native zero color value, usually black for DeviceGray/RGB and white for DeviceCMYK.
- Lists affected areas such as `alphaimage`, `readimage`, color mapping, images, and compositing code.
- Provides a disabled `PREMULTIPLY_TOWARDS_WHITE` preprocessor option.

Behavior:
- No active functions or data structures; this is a policy/configuration header.

Dependencies:
- None beyond normal include guard context.

Notable risks:
- Boundary inconsistency is acknowledged in comments because device color-space conventions differ.
