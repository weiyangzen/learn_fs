# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/i2c/controller.h

## Role

`i2c/controller.h` defines the kernel provider API for I2C, I3C, and SMBus controller drivers.

## Key Interfaces and Data

- Provider version constants are `I2C_CTRL_PROVIDER_V0` and `I2C_CTRL_PROVIDER`.
- `i2c_ctrl_ops_t` contains callbacks for port naming, SMBus I/O, I2C I/O, property info, property get, and property set.
- `i2c_ctrl_register_t` describes controller version, type, name, number of ports, devinfo, driver-private pointer, and ops.
- `i2c_ctrl_hdl_t` is the opaque registration handle.
- `i2c_ctrl_reg_error_t` enumerates registration validation failures: bad version, null args, bad/missing ops, bad type, unsupported type, bad devinfo, bad ports/name, internal errors, bad module type, nexus errors, non-unique registration, required property errors, and bad property values.
- Module init/fini hooks patch devops for controller modules.
- Alloc/free/register/unregister functions manage controller registration.
- `i2c_ctrl_port_name_portno()` provides default port naming.
- `i2c_ctrl_io_success()` and `i2c_ctrl_io_error()` fill `i2c_error_t`.
- Property info helpers set permissions, default values, numeric ranges, and bit positions.
- `i2c_ctrl_timeout_t` identifies framework-provided timeout classes for I/O, controller polling, bus activation, and abort completion.
- Timeout count/delay helpers return controller-specific retry parameters.

## Dependencies and Use

Controller drivers include this header instead of the client or mux API. It builds on shared request/error/property types from `i2c.h`.

## Research Notes

Registration is defensive and validation-heavy, reflecting that controller capabilities and required properties become part of the visible I2C nexus.
