# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/i2c/mux.h

## Role

`i2c/mux.h` defines the kernel provider API for I2C mux drivers, including in-band, out-of-band, and other mux control styles.

## Key Interfaces and Data

- Provider version constants are `I2C_MUX_PROVIDER_V0` and `I2C_MUX_PROVIDER`.
- `I2C_MUX_PORT_ALL` is `UINT32_MAX` and indicates all ports should be disabled.
- `i2c_mux_ops_t` callbacks name ports, enable one port, and disable one or all ports. Enable/disable receive an optional transaction and fill `i2c_error_t`.
- `i2c_mux_register_t` describes version, number of ports, devinfo, driver-private pointer, and ops. The typedef name has a visible spelling typo in the struct tag: `i2c_mux_regiser`.
- `i2c_mux_hdl_t` is the opaque registration handle.
- `i2c_mux_reg_error_t` enumerates registration failures: bad version, ports, devinfo, bus, ops, unsupported devinfo, existing registration, nexus error, and busy.
- Module init/fini, register allocation/free, register, and unregister functions mirror the controller provider API.
- Default port naming helpers support zero-based and one-based numeric port names.
- `i2c_io_error()` is a mux-facing helper for setting errors.

## Dependencies and Use

The header includes `i2c/client.h` because mux drivers may themselves be I2C clients when controlled in-band.

## Research Notes

The framework requires only one active downstream segment at a time. Mux enable operations are allowed to replace an already active segment.
