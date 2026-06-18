# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/gpio/kgpio.h

## Role

`kgpio.h` defines the user/kernel ioctl ABI for the kernel GPIO framework.

## Key Interfaces and Data

- `KGPIO_IOC` is the ioctl command base.
- `KGPIO_IOC_CTRL_INFO` returns `kgpio_ctrl_info_t`: group count, GPIO count, DPIO count, padding, and controller device path.
- `KGPIO_IOC_GPIO_INFO` uses `kgpio_gpio_info_t` to query one GPIO's ID, flags, packed attribute nvlist pointer, and length. `KGPIO_GPIO_F_DPIO` marks a GPIO with a DPIO.
- `KGPIO_IOC_GPIO_UPDATE` uses `kgpio_update_t` to set attributes via nvlist and return an error nvlist. Flags indicate whether errors occurred and whether the error nvlist is valid.
- `KGPIO_IOC_DPIO_CREATE` uses `kgpio_dpio_create_t` to create a DPIO from a GPIO ID with read/write/kernel flags and a short name.
- `KGPIO_IOC_DPIO_DESTROY` destroys the DPIO bound to a GPIO ID.
- `KGPIO_IOC_GPIO_NAME2ID` maps a GPIO name to an ID.
- Kernel-only 32-bit forms `kgpio_gpio_info32_t` and `kgpio_update32_t` translate pointer/size fields for ILP32 callers.

## Dependencies and Use

The header includes `kgpio_attr.h` and standard integer/path limits. Attribute payloads are nvlists passed through user pointers rather than fixed structs.

## Research Notes

KGPIO separates controller discovery, GPIO attribute inspection/update, and DPIO creation. The ABI is pointer-heavy, so 32-bit compatibility structs are required.
