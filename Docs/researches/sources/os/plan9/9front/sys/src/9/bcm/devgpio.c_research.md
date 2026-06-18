# File Research: sources/os/plan9/9front/sys/src/9/bcm/devgpio.c

Plan 9 GPIO device `#G` for Raspberry Pi pins.

Key behavior:
- Encodes file, parent, naming scheme, and pin number in Qid paths.
- Supports BCM, board, WiringPi, and generic naming schemes with revision-dependent pin tables.
- Exposes `gpio` directory, pin data files, `ctl`, and `event`.
- Data files read/write pin level as `0` or `1`.
- `ctl` supports scheme selection, pin function, pull control, and edge event configuration.
- Registers a GPIO interrupt handler that records edge events into a 32-bit event mask and wakes readers.
- Allows only one event reader at a time.

Dependencies:
- Uses low-level GPIO operations from `gpio.c` and Plan 9 command parsing/device helpers.

Research notes:
- Event reads return raw bytes from the 32-bit event mask and clear on wrapped offsets.
