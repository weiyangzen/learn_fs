# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/gpio/pca953x.h

## Role

`pca953x.h` defines KGPIO attributes for PCA953x-family GPIO expanders.

## Key Interfaces and Data

- `PCA953X_GPIO_ATTR_INPUT` is read-only and uses `pca953x_gpio_input_t`: low or high.
- `PCA953X_GPIO_ATTR_OUTPUT` is read/write and uses `pca953x_gpio_output_t`: disabled, low, or high. Disabled makes the pin input-only.
- `PCA953X_GPIO_ATTR_POLARITY` is read/write and uses `pca953x_gpio_polarity_t`: normal or inverted input polarity.
- The comments also identify `KGPIO_ATTR_NAME` as a standard supported attribute.

## Dependencies and Use

This header is a provider-specific attribute definition layer over KGPIO. Values are transported as `uint32_t` enum values in attribute nvlists.

## Research Notes

The PCA953x interface focuses on three hardware concepts: input state, output latch/configuration, and input polarity inversion.
