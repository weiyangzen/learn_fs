# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/i2c/i2c.h

## Role

`i2c/i2c.h` defines shared I2C, SMBus, and I3C-adjacent data types used by kernel controllers, kernel clients, mux drivers, and private userland ioctl/libi2c code.

## Key Interfaces and Data

- `i2c_speed_t` is a bitfield of standard, fast, fast-plus, high-speed, and ultra-fast bus speeds.
- `i2c_ctrl_type_t` distinguishes I2C, I3C, and SMBus controllers.
- `i2c_errno_t` is a large error taxonomy grouped by core errors, ioctl errors, client-driver errors, property errors, and mux errors.
- Core errors cover controller failure, address validation, reserved/in-use addresses, request translation, missing read/write, bad I2C/SMBus request shape, unsupported SMBus ops, and lock interruption/nonblock failure.
- Ioctl errors cover nvlist size/parse/key problems, bad user pointers, memory, device naming, compatible-list limits, nexus failures, bus-lock conflicts, in-progress operations, and bad devinfo.
- Client errors cover reg index, flags, signals, register-access attributes, unsupported register addressing, bad register ranges/counts, partial registers, and shared-address misuse.
- Property errors cover unsupported/unknown/read-only properties, buffer sizing, bad values, and unsupported sets.
- `i2c_ctrl_error_t` captures controller-detected I/O failures such as internal/driver errors, unsupported commands, bus busy, address/data/generic NACK, arbitration lost, bad ACK, request timeout, bad SMBus block length, and SMBus clock-low timeout.
- `i2c_error_t` pairs a core error with controller error detail.
- `I2C_NAME_MAX` is 32.
- `i2c_addr_type_t` supports 7-bit and 10-bit addresses; `i2c_addr_t` stores type and address.
- `i2c_addr_source_t` identifies addresses from `reg[]`, claimed, or shared-claimed origins.
- `i2c_rsvd_addr_t` names reserved 7-bit address ranges.
- Request sizing constants include SMBus v2/v3 block limits and `I2C_REQ_MAX` of 256 bytes.
- `smbus_op_t` enumerates SMBus operations from quick command through block operations, host notify, 32/64-bit SMBus 3.x operations, and I2C-compatible block transfers.
- `i2c_req_flags_t` includes poll and quick-write flags.
- `smbus_req_t` and `i2c_req_t` carry error state, operation/flags, address, read/write lengths, command where applicable, and 256-byte data buffers.
- Property types support scalar `uint32_t` and bitfield `uint32_t`; permissions are read-only or read/write.
- Property range structures describe allowed u32 ranges or bit masks.
- `i2c_prop_t` enumerates standard controller properties: bus speed, port count, type, supported SMBus ops, max read/write/block sizes, and timing parameters.
- `smbus_prop_op_t` converts each SMBus op enum into a supported-operation bit.
- Property name and value size limits are 32 and 256 bytes.

## Dependencies and Use

This is the common base included by `client.h`, `controller.h`, `mux.h`, and `ioctl.h`. It intentionally avoids kernel-only dependencies beyond standard integer/bool types.

## Research Notes

The header is a new, strongly typed ABI surface. Its most important contribution is not request structs alone, but the detailed, layered error taxonomy that lets clients distinguish framework, ioctl, controller, property, and mux failures.
