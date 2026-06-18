# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/gpio/gpio_sim.h

## Role

`gpio_sim.h` defines attributes for the synthetic GPIO simulator driver used for testing.

## Key Interfaces and Data

- Documents standard `KGPIO_ATTR_NAME` as a read-only semantic GPIO name.
- `GPIO_SIM_ATTR_OUTPUT` is a read/write `uint32_t` using `gpio_sim_output_t`: disabled, low, high.
- `GPIO_SIM_ATTR_INPUT` is a read-only `uint32_t` using `gpio_sim_input_t`: low or high.
- `GPIO_SIM_ATTR_PULL` is read/write using `gpio_sim_pull_t`: disabled, down, specific down/up strengths, up, and both.
- `GPIO_SIM_ATTR_VOLTAGE` is read-only using `gpio_sim_voltage_t`: 1.8 V, 3.3 V, 12.0 V, or 54.5 V.
- `GPIO_SIM_ATTR_SPEED` is read/write using `gpio_sim_speed_t`: low, medium, high, very high.

## Dependencies and Use

The header only defines simulator attribute names and enums; actual transport is the KGPIO nvlist attribute interface.

## Research Notes

The simulator intentionally exposes more attributes than a minimal GPIO, giving tests coverage for read-only, read/write, string, scalar, and enumerated values.
