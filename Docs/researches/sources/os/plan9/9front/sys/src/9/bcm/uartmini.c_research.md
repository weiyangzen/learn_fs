# File Research: sources/os/plan9/9front/sys/src/9/bcm/uartmini.c

BCM auxiliary mini-UART driver.

Key responsibilities:
- Maps AUX registers at `VIRTIO+0x215000`.
- Configures GPIO pins 14/15 for TX/RX.
- Implements UART operations for enable/disable, interrupt receive/transmit, kick, break, baud, word bits, stop bits, parity, modem control, and polled get/put.
- Registers a `PhysUart` for Plan 9 serial core.

Important behavior:
- Baud divisor is computed from core clock.
- Only 7/8-bit modes are meaningful; parity/stop/modem functions are mostly constrained by hardware.
- Interrupt handler drains RX and fills TX while status bits allow.

Dependencies:
- UART core, GPIO setup, interrupt registration, and clock mailbox helpers.
