# File Research: sources/os/plan9/9front/sys/src/9/bcm/devarch.c

BCM `#P` architecture device and console UART setup.

Key behavior:
- Provides dynamic registration for architecture files with read/write callbacks.
- Exposes `cputype` and `cputemp` files.
- Implements the Plan 9 device methods for `#P`.
- Selects console UART from `console` config, enables it if needed, applies line settings, and replays buffered kernel messages.
- Controls the activity LED through firmware virtual GPIO or a configured GPIO pin.

Dependencies:
- Uses `addarchfile`, UART physical device table, GPIO helpers, firmware temperature, and config access.

Research notes:
- `okay` honors Raspberry Pi firmware config keys for LED GPIO and active-low polarity.
