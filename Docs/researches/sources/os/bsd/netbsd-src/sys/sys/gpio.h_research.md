# File Research: sources/os/bsd/netbsd-src/sys/sys/gpio.h

Read completely: 151 lines.

## Purpose
Defines the GPIO user ioctl ABI, pin configuration flags, interrupt flags, and compatibility structures.

## Main Interfaces
- Pin states: `GPIO_PIN_LOW`, `GPIO_PIN_HIGH`.
- `GPIOMAXNAME`.
- Configuration flags: input/output/inout, open-drain, push-pull, tristate, pull-up/down, inversion, user access, pulsate, alternate functions.
- Interrupt flags and masks: edge/level modes, `GPIO_INTR_MPSAFE`.
- Structures: `gpio_info`, `gpio_req`, `gpio_set`, `gpio_attach`.
- Ioctls: `GPIOINFO`, `GPIOSET`, `GPIOUNSET`, `GPIOREAD`, `GPIOWRITE`, `GPIOTOGGLE`, `GPIOATTACH`.
- `COMPAT_50` old structs and ioctls.

## Dependencies And Integration
Uses ioctl encoding and time header. Consumed by gpio device drivers and userland tools.

## Risks And Edge Cases
- Compatibility ioctls preserve old ABI.
- Pin names are fixed-size buffers.
- Hardware capabilities and requested flags must be validated by drivers.

## Filesystem Relevance
Low. Device-control ABI, not filesystem code.
