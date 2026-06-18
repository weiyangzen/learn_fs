# File Research: sources/os/plan9/9front/sys/src/9/port/devi2c.c

Purpose: I2C bus device `#J`, exposing registered I2C buses and probed devices as ctl/data files and providing kernel helper functions for common I2C transactions.

Exposed interface: `#J/<bus>/i2c.<addr>.ctl` and `i2c.<addr>.data`. `ctl` supports `size` and `subaddress`. `data` reads/writes device payloads with optional subaddress offset.

Core implementation: global arrays track up to 16 buses and 1024 devices. `addi2cbus` and `addi2cdev` register objects. `probebus` initializes a bus once and probes 7-bit addresses 0x08-0x77 plus all 10-bit addresses, creating copied `I2Cdev` records for responding addresses. `i2cgen` builds the synthetic hierarchy.

Transaction helpers: `putaddr` encodes 7-bit/10-bit address and optional subaddress. `i2csend`, `i2crecv`, quick, byte, word, and 32-bit helpers build small packets and call `i2cbusio`. `i2cbusio` serializes access with qlock/canqlock depending on context and calls the bus `io` callback.

Dependencies: `i2c.h` bus/device structures and callbacks.

Research notes: review should focus on bus probing side effects, fixed packet buffer size truncation, subaddress byte order, user/non-user locking behavior, and consistency of the `devs` array while generating directories.
