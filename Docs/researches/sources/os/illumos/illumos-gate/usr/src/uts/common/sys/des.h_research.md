# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/des.h

This header defines the generic, hardware-independent DES driver ioctl interface. It includes `sys/ioccom.h`.

It defines maximum block operation length (`DES_MAXLEN`) and quick inline data length (`DES_QUICKLEN`). Direction enum values are encrypt and decrypt; mode enum values are CBC and ECB.

`struct desparams` contains the 8-byte key, direction, mode, 8-byte initialization vector, data length, and a union that either embeds quick data or points to a larger buffer. Macros alias the union members as `des_data` and `des_buf`.

Two ioctls are defined: `DESIOCBLOCK` for arbitrary-sized buffers and `DESIOCQUICK` for small data passed directly in the structure.

Research notes:
- This is a legacy crypto ioctl ABI, not modern kernel crypto framework API.
- Structure layout and ioctl numbers are user-visible.
