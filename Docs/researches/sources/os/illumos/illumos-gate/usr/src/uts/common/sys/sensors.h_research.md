# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sensors.h

## Role

Defines evolving consolidated sensor ioctl structures and kernel sensor registration interfaces.

## Key Interfaces

- Sensor kinds: unknown, temperature, voltage, current, and synthetic.
- Sensor units: unknown, Celsius, Fahrenheit, Kelvin, volts, amps, and none.
- Ioctl namespace `SENSOR_IOCTL`, with `SENSOR_IOCTL_KIND` and `SENSOR_IOCTL_SCALAR`.
- `sensor_ioctl_kind_t` reports kind and derivation.
- `sensor_ioctl_scalar_t` reports unit, signed granularity, precision, padding, and signed value.
- Kernel callback types `ksensor_kind_f` and `ksensor_scalar_f`.
- `ksensor_ops_t` groups kind and scalar callbacks.
- Kernel helpers create typed sensors, PCI scalar sensors, and remove one or all sensor IDs.

## Semantics

Scalar values are expressed through `sis_value` plus signed `sis_gran`: positive granularity divides the value into subunits; negative granularity multiplies.

## Risk Notes

The file explicitly marks these interfaces unstable. Consumers should expect ioctl and kernel API evolution.
