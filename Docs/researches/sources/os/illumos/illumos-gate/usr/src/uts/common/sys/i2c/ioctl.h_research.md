# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/i2c/ioctl.h

## Role

`i2c/ioctl.h` defines private userland ioctl structures for libi2c and the user-visible I2C nexus/control devices.

## Key Interfaces and Data

- `I2C_NEXUS_TYPE_PROP` and values identify whether a node is a port, controller, or mux.
- `UI2C_IOCTL` is the ioctl command base.
- Controller property ioctls:
  - `UI2C_IOCTL_CTRL_NPROPS`
  - `UI2C_IOCTL_CTRL_PROP_INFO`
  - `UI2C_IOCTL_CTRL_PROP_GET`
  - `UI2C_IOCTL_CTRL_PROP_SET`
- `ui2c_ctrl_nprops_t` reports standard and private property counts.
- `ui2c_prop_info_t` reports property error, ID, type, permissions, default/possible lengths, name, default bytes, and possible bytes.
- `ui2c_prop_t` gets/sets property values with an embedded `i2c_error_t`.
- Device add/remove ioctls use packed nvlists for add and `i2c_addr_t` for remove. Nvlist key constants define address, type, name, compatible list, max nvlist size, and max compatible count.
- `UI2C_IOCTL_I2C_REQ` and `UI2C_IOCTL_SMBUS_REQ` send raw I2C/SMBus requests using shared request structs.
- `UI2C_IOCTL_PORT_INFO` returns port number and address occupancy for 7-bit addresses, including downstream presence and major number.
- `UI2C_IOCTL_DEV_INFO` returns primary address, mux flag, and 7-bit address usage for a device.
- `UI2C_IOCTL_MUX_INFO` returns mux port count.
- `_KERNEL && _SYSCALL32` defines packed `ui2c_dev_add32_t` for 32-bit pointer/size translation.

## Dependencies and Use

The comments state this is private to libi2c and may change. It includes shared `i2c.h` request and property definitions.

## Research Notes

The ABI uses fixed-size arrays for properties and 7-bit address maps but nvlists for device creation, anticipating future extension of device metadata.
