# File Research: sources/os/plan9/9front/sys/src/9/imx8/lcd.c

Role: i.MX8 LCDIF + MIPI DSI + SN65DSI86 bridge + PWM backlight display initialization and blanking.

Key responsibilities:
- Defines reset-controller, PWM2, MIPI DPHY, DSI host, and LCDIF register bits.
- Models video timing and derived DSI timing configuration.
- Computes DSI/DPHY timing parameters from lane count, HS clock, ref clock, and escape clocks.
- Resets and initializes LCDIF for 24-bit dotclock mode, framebuffer address, sync timings, and frame-done interrupt.
- Initializes SN65DSI86 bridge over I2C, including reset, PLL clock selection, lane/rate setup, ASSR, link training, detailed timing registers, and stream enable.
- Reads EDID through bridge AUX passthrough and parses the first detailed timing descriptor.
- Programs DPHY magic/timing/PLL settings and waits for lock.
- Programs DSI host lane, clock, timeout, and DPI video parameters.
- Sets up backlight GPIO and PWM2.
- Implements `blankscreen()` by toggling LCDIF clocks/run state, PWM/backlight GPIO, and bridge video output.
- `lcdinit()` sequences IRQ setup, GPR display mux, backlight, bridge enable, MIPI power/reset/clock setup, EDID, framebuffer allocation, pixel clock, bridge, and LCDIF start.

Dependencies:
- Uses I2C, IOMUX, GPIO, CCM, GPC, screen framebuffer API, Plan 9 draw/memdraw, and GIC interrupts.

Notes and risks:
- DSI HS clock is fixed for the bridge at `2*486 MHz`.
- `dpiinit()` comments that VSYNC/HSYNC polarity programming "seems wrong"; it writes zero regardless of EDID polarity.
- Failure paths print `lcdinit: <reason>` and leave display unavailable.
