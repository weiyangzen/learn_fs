# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/snarf.c

Connects panels to the Plan 9 snarf buffer.

Key behavior:
- `plputsnarf()` writes non-empty strings to `/dev/snarf`.
- `plgetsnarf()` reads all available snarf data into a NUL-terminated buffer.
- `plsnarf()` invokes a panel’s `snarf` method and writes the result.
- `plpaste()` reads snarf data and passes it to a panel’s `paste` method.

Important dependencies: `/dev/snarf`, panel snarf/paste callbacks.

Notable risks:
- Snarf data is treated as byte strings; panel-specific paste methods handle UTF conversion.
