# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcvalue.h

Device color-value scalar definition and conversion macros.

Key contents:
- Defines `gx_color_value` as `unsigned short`.
- Defines size/bits/max constants for device color values.
- Provides byte conversion macros `gx_color_value_to_byte` and `gx_color_value_from_byte`.
- Provides fraction conversion macros `frac2cv` and `cv2frac`.

Notable dependencies:
- Assumes fraction conversion helpers such as `frac2ushort` and `ushort2frac` are already available to includers.

Research notes:
- Device color values are currently 16-bit, with comments allowing the possibility of fewer effective bits in the future.
- This type is used across device encode/decode and color mapping paths.
