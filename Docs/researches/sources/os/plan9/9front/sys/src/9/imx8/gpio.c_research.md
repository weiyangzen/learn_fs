# File Research: sources/os/plan9/9front/sys/src/9/imx8/gpio.c

Role: i.MX8 GPIO bank driver with input/output helpers and callback-based interrupt dispatch.

Key responsibilities:
- Defines GPIO data, direction, interrupt config, mask/status, and edge-select register offsets.
- Models five GPIO banks with MMIO base and clock-gate name.
- Lazily enables each bank clock, disables its interrupt mask, caches direction, and marks it enabled.
- `gpioout()` switches a pin to output and sets/clears the data bit.
- `gpioin()` switches a pin to input and reads the data register.
- `gpiointrenable()` configures pin input mode, edge/level trigger registers, stores callback, and unmasks the pin.
- `gpiointrdisable()` masks a pin and clears its callback.
- `gpiointerrupt()` acknowledges pending status and invokes callbacks with encoded pin IDs.
- `gpiolink()` registers low/high IRQs for all five banks.

Dependencies:
- Uses `setclkgate`, GIC interrupts, `GPIO_PIN`, and platform GPIO mode constants.

Notes and risks:
- Pin bank encoding is one-based in callers (`GPIO_PIN(1, 14)`), and `enable()` rejects bank 0.
- In `gpiointrenable()`, the code compares and shifts using `bit` rather than pin index for ICR1/ICR2 selection; this is source behavior and should be treated carefully if modifying interrupt modes.
