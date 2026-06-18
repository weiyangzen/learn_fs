# File Research: sources/os/bsd/openbsd-src/sys/sys/gpio.h

This header defines the GPIO ioctl ABI.

Key definitions:
- Pin values: `GPIO_PIN_LOW`, `GPIO_PIN_HIGH`.
- Name length: `GPIOPINMAXNAME`.
- Pin capability/config flags: input/output/inout, open-drain, push-pull, tristate, pullup/pulldown, input/output inversion, user access, securelevel set marker.
- Structures: `gpio_info`, `gpio_pin_op`, `gpio_pin_set`, `gpio_attach`.
- Ioctls: `GPIOINFO`, `GPIOPINREAD`, `GPIOPINWRITE`, `GPIOPINTOGGLE`, `GPIOPINSET`, `GPIOPINUNSET`, `GPIOATTACH`, `GPIODETACH`.

Risk notes:
- GPIO configuration affects hardware pins and can expose user access through `GPIO_PIN_USER`.
- Attach/detach passes device names and masks through ioctl ABI, so driver name length and pin offsets are fixed.
