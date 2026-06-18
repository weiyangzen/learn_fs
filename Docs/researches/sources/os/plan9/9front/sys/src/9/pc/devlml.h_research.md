# File Research: sources/os/plan9/9front/sys/src/9/pc/devlml.h

Hardware constants and shared-memory structures for the LML33 Motion JPEG driver.

Key contents:
- Defines driver version, maximum LML cards, timing constants, and Zoran vendor/device IDs.
- Defines I2C, interrupt, and register offsets used by `devlml.c`.
- Defines JPEG marker constants and `FrameHeader` layout embedded in captured buffers.
- Defines four-fragment capture buffering, fragment descriptor structures, and `CodeData` shared with hardware.
- Provides rounded `Codedatasize` and `Grabdatasize` constants.

Role:
- Captures the hardware ABI for Zoran/LML frame buffers and descriptors; comments warn not to alter the hardware-used struct layouts.

Dependencies:
- Used directly by `devlml.c` and depends on kernel page size constants/types.

Notable constraints:
- `FrameHeader`, `FragmentTable`, and `CodeData` layouts are hardware-facing and must remain stable.
