# File Research: sources/os/bsd/netbsd-src/lib/lua/gpio/gpio.c

## Summary
Implements a Lua binding for NetBSD GPIO devices. It exposes a module-level `open()` and per-device userdata methods for GPIO info, pin configuration, read/write/toggle, attach, and close.

## Main Responsibilities
- Open GPIO device paths with `O_RDWR` and store fds in Lua userdata.
- Close fds explicitly or from `__gc`.
- Convert Lua pin arguments from integer pin numbers or string pin names into GPIO request structures.
- Issue GPIO ioctls: `GPIOINFO`, `GPIOSET`, `GPIOUNSET`, `GPIOREAD`, `GPIOWRITE`, `GPIOTOGGLE`, and `GPIOATTACH`.
- Export GPIO pin state and configuration constants.
- Add module metadata fields `_COPYRIGHT`, `_DESCRIPTION`, and `_VERSION`.

## Key Interfaces
- `luaopen_gpio(lua_State *L)`.
- Lua methods: `open`, `info`, `close`, `set`, `unset`, `read`, `write`, `toggle`, `attach`.

## Risks
Most ioctl failure messages only include the operation name, not `strerror(errno)`. `gpio_open()` uses stack-relative indices after creating userdata, so call order assumptions are important. Access requires permissions on GPIO device nodes and can mutate hardware state.
