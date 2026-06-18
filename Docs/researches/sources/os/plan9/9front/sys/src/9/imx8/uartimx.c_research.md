# File Research: sources/os/plan9/9front/sys/src/9/imx8/uartimx.c

Role: i.MX8 UART1 driver integrated with Plan 9 `PhysUart`.

Key responsibilities:
- Defines UART register layout and control/status bits.
- Instantiates one UART at `VIRTIO + 0x860000`, default 115200 baud, 25 MHz source.
- Implements transmit kicking with staged output and TRDY interrupt enable/disable.
- Configures UART enable, parity, stop bits, word size, RX/TX enable, FIFO thresholds, and baud modulator registers.
- Supports `bits`, `stop`, `parity`, and `baud` control by updating the `Uart` state then reconfiguring hardware.
- Interrupt handler drains RX chars and kicks TX.
- Clock helper programs `<uart>.ipg_perclk` from oscillator and gates it.
- `enable()` optionally registers `IRQuart1` interrupt, enables clock, and configures hardware.
- `disable()` avoids disabling the console UART to prevent glitches.
- Provides polling console `getc`/`putc` and `uartconsinit()`.

Dependencies:
- Plan 9 UART framework, CCM, GIC, `VIRTIO` MMIO mapping.

Notes:
- Only UART1 is exposed by `pnp()`.
- RTS, DTR, FIFO, modem control, and break are no-op.
