# File Research: sources/os/plan9/9front/sys/src/9/imx8/i2cimx.c

Role: i.MX8 I2C controller driver integrated with Plan 9 `I2Cbus`.

Key responsibilities:
- Defines i.MX I2C registers/status/control bits and four controller MMIO/IRQ structs.
- Provides interrupt wakeup and `waitsr()` that can poll at high priority or sleep on a rendezvous in process context.
- Implements combined write/read transfers with start, repeated start, ACK/NACK handling, dummy read, stop, arbitration-lost handling, and byte count return.
- Supports 7-bit and apparent extended address prefix sizing via `alen`.
- Selects IFDR divider index from a hardware divider table.
- Enables module clocks by setting `<bus>.ipg_clk_patref` to 25 MHz and gating it.
- Registers I2C1, I2C3, and I2C4 at 400 kHz and configures their pads.

Dependencies:
- Plan 9 `../port/i2c.h`, `iomuxpad`, CCM, GIC interrupt registration.

Notes:
- I2C2 controller struct exists but is not registered by `i2cimxlink()`.
- `waitsr()` clears interrupt/arbitration bits as part of polling.
