# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/gpio/zen_gpio.h

## Role

`zen_gpio.h` defines KGPIO attributes for AMD Zen-family GPIO controllers, covering identification, output/input state, electrical configuration, debounce, interrupt trigger, status, and raw register inspection.

## Key Interfaces and Data

- Identification attributes:
  - `ZEN_GPIO_ATTR_PAD_NAME`
  - `ZEN_GPIO_ATTR_PAD_TYPE`
  - `ZEN_GPIO_ATTR_PIN`
  - `ZEN_GPIO_ATTR_CAPS`
- `zen_gpio_pad_type_t` distinguishes GPIO, SD, I2C, and I3C pads.
- `zen_gpio_cap_t` flags interrupt-capable AGPIO and remote-block GPIOs.
- `ZEN_GPIO_ATTR_OUTPUT_DRIVER` reports push-pull/open-drain/unknown driver mode.
- `ZEN_GPIO_ATTR_OUTPUT` controls disabled/low/high output; open-drain pins only validly support disabled and low.
- `ZEN_GPIO_ATTR_INPUT` reports low/high input.
- `ZEN_GPIO_ATTR_VOLTAGE` reports supported voltage rails as a bitfield.
- `ZEN_GPIO_ATTR_PULL` controls pull configuration, including disabled, down, up strengths, and illegal-but-observable hardware combinations.
- `ZEN_GPIO_ATTR_DRIVE_STRENGTH` controls/report drive strength: unknown, 40, 60, or 80 ohm.
- Debounce attributes are `ZEN_GPIO_ATTR_DEBOUNCE_MODE`, `ZEN_GPIO_ATTR_DEBOUNCE_UNIT`, and `ZEN_GPIO_ATTR_DEBOUNCE_COUNT`, with RTC-derived units.
- `ZEN_GPIO_ATTR_TRIGGER_MODE` covers edge/level interrupt trigger modes and polarity.
- `ZEN_GPIO_ATTR_STATUS` reports wake and interrupt status bits.
- `ZEN_GPIO_ATTR_RAW_REG` exposes the raw GPIO register for debugging.

## Dependencies and Use

This is entirely an attribute vocabulary for the KGPIO nvlist framework. Comments indicate it covers most Zen 1 through Zen 4 GPIOs.

## Research Notes

Some hardware features are intentionally exposed read-only, especially interrupt/wake-related state, because the driver does not expect arbitrary user manipulation.
