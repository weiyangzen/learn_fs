# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/gpio/kgpio_attr.h

## Role

`kgpio_attr.h` defines shared GPIO attribute vocabulary and standard attribute-update error codes.

## Key Interfaces and Data

- Standard attribute keys:
  - `KGPIO_ATTR_NAME`
  - `KGPIO_ATTR_META`
  - `KGPIO_ATTR_PROT`
  - `KGPIO_ATTR_POS`
- `kgpio_prot_t` distinguishes read-only and read/write attributes.
- `kgpio_attr_err_t` describes per-attribute update outcomes: OK, read-only, unknown attribute, bad type, unknown value, and value known but not applicable to this GPIO/current configuration.

## Dependencies and Use

The header is shared by userland-facing KGPIO ioctl definitions and provider-specific attribute headers. It assumes attributes are represented as nvlists.

## Research Notes

The comments note that possible values are currently fully enumerated, with future range support considered.
