# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icremap.h

Defines interpreter color-remapping callback state.

Key points:
- Defines `int_remap_color_info_t`.
- Stores an interpreter remapping procedure and tint values up to `GS_CLIENT_COLOR_MAX_COMPONENTS`.
- Comments note pattern remapping ignores tint values, while DeviceN remapping uses them.
- Provides a simple GC descriptor macro.

Research notes:
- This is small state passed between graphics color remapping and interpreter procedures.
