# File Research: sources/os/plan9/9front/sys/src/9/bcm/i2cbcm.c

Broadcom Serial Controller I2C driver for Raspberry Pi BCM2835-family 32-bit kernels.

Key responsibilities:
- Registers an `I2Cbus` named `i2c1` with `addi2cbus()`.
- Maps BSC registers at `VIRTIO+0x804000`.
- Configures GPIO pins 2 and 3 for SDA/SCL alternate function with pull-ups.
- Sets the controller clock divider from `getclkrate(ClkCore)` for 100 kHz target timing.
- Handles I2C interrupts for RX, TX, and transfer-done conditions.
- Implements `i2cio()` for simple read/write transactions through the FIFO.

Important behavior:
- Rejects subaddressed and 10-bit-address transactions.
- Treats one-byte write probes specially to avoid controller NAK behavior.
- Uses `Rendez` sleep/wakeup around FIFO-ready and done bits.
- Clears controller state and returns `-1` on NAK or clock-stretch timeout.

Dependencies:
- Plan 9 I2C core, GPIO helpers, clock mailbox helpers, interrupt registration, and BCM IRQ numbers.
