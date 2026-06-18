# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/i2c/client.h

## Role

`i2c/client.h` defines the kernel client-driver API for devices attached to I2C/SMBus/I3C ports.

## Key Interfaces and Data

- Opaque types: `i2c_client_t`, `i2c_reg_hdl_t`, and `i2c_txn_t`.
- `i2c_client_init()` creates a client for a `dev_info_t` and reg index; `i2c_client_destroy()` releases it.
- `i2c_client_claim_addr()` allows devices to claim additional exclusive or shared addresses; `I2C_CLAIM_F_SHARED` restricts sharing to instances of the same driver.
- `i2c_client_addr()` returns a client's address.
- Bus locking is represented by `i2c_txn_t`; `i2c_bus_lock()` can use `I2C_BUS_LOCK_F_NONBLOCK`, and `i2c_bus_unlock()` releases it. Passing NULL transactions to I/O helpers makes them lock for one operation.
- `i2c_reg_acc_attr_t` describes register access version, flags, address/register byte lengths, endian attributes, and maximum device address.
- Register handle functions initialize/destroy register access helpers.
- `i2c_reg_get()` and `i2c_reg_put()` read/write auto-incrementing device registers.
- `i2c_reg_max_read()` and `i2c_reg_max_write()` expose controller-backed transfer limits.
- SMBus convenience helpers implement send byte, write/read 8-bit, write/read 16-bit, and receive byte operations.
- Error string helpers map core and controller errors to text.
- `i2c_client_ksensor_create_scalar()` creates scalar kernel sensors for I2C devices.

## Dependencies and Use

The header includes devops, stdint/stdbool, shared `i2c.h`, and sensors. It assumes the `dev_info_t` passed is the caller's node or otherwise held by the caller.

## Research Notes

The API encourages register-oriented access for most drivers, with explicit transaction objects only when a sequence must hold the bus across multiple operations.
