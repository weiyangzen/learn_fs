# File Research: sources/os/plan9/9front/sys/src/9/port/i2c.h

Generic I2C/SMBus interface header for controller and device registration plus common transfer helpers.

Key contents:
- Defines `I2Cbus` with name, speed, private controller pointer, init callback, combined I/O callback, probe flag, and `QLock`.
- Defines `I2Cdev` with bus pointer, 10-bit-address flag, address, subaddress, and device size.
- Declares bus/device registration and lookup APIs.
- Declares generic send/receive helpers over addressable devices.
- Declares SMBus-style quick, byte, word, and 32-bit read/write helpers.

Role:
- Keeps controller drivers, device clients, and generic SMBus helpers behind a small portable interface.

Notable constraints:
- The core bus operation is one callback `io(dev, pkt, olen, ilen)`, so controller implementations own transaction semantics.
