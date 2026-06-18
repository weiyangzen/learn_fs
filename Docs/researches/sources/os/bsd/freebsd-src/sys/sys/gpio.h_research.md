# File Research: sources/os/bsd/freebsd-src/sys/sys/gpio.h

## Purpose
Defines GPIO pin state/configuration flags, ioctl argument structures, event reporting formats, and GPIO control ioctls.

## Main Interfaces
- Pin states: `GPIO_PIN_LOW`, `GPIO_PIN_HIGH`.
- Name limit: `GPIOMAXNAME`.
- Pin flags for direction, drive mode, pullups, inversion, pulsate, preset output state.
- Interrupt flags: level/edge modes, attached state, masks.
- `struct gpio_pin`: pin number, name, caps, flags.
- `struct gpio_req`: pin number and value.
- Event reporting:
  - `struct gpio_event_detail`
  - `struct gpio_event_summary`
  - `struct gpio_event_config`
  - report types `GPIO_EVENT_REPORT_DETAIL`, `GPIO_EVENT_REPORT_SUMMARY`
- Batch operations:
  - `struct gpio_access_32`
  - `struct gpio_config_32`
- Ioctls: `GPIOMAXPIN`, `GPIOGETCONFIG`, `GPIOSETCONFIG`, `GPIOGET`, `GPIOSET`, `GPIOTOGGLE`, `GPIOSETNAME`, `GPIOACCESS32`, `GPIOCONFIG32`, `GPIOCONFIGEVENTS`.

## Dependencies And Integration
Includes `ioccom.h` and userland `stdbool.h` outside kernel/standalone. Batch operations assume driver-specific mapping of adjacent pins to 32-bit words.

## Risk Notes
The event structures include `bool`, so ABI layout must be checked across architectures. Atomicity promises for `GPIOACCESS32` are strict; `GPIOCONFIG32` explicitly allows best-effort non-atomic hardware behavior.
