# File Research: sources/os/plan9/9front/sys/src/9/imx8/devrtc.c

Role: Plan 9 `#r/rtc` device for an NXP PCF8523 RTC on I2C.

Key responsibilities:
- Attaches to `i2c3` address `0x68`, configures 1-byte subaddresses, and exposes a single `rtc` file.
- Reads PCF8523 BCD time registers seconds through year.
- Converts BCD fields to seconds since 1970 with 1970/2000 century split.
- Performs stable reads by requiring two consecutive equal second values, retrying up to 100 times.
- Allows only `eve` to write non-read mode.
- Parses written numeric seconds, converts to RTC fields, BCD-encodes them, and writes the clock registers.
- Implements local `rtc2sec()`, `sec2rtc()`, and leap-year helpers.

Dependencies:
- Uses Plan 9 device framework, `../port/i2c.h`, `i2cdev`, `i2crecv`, `i2csend`, and common device helpers.

Notes and risks:
- Write path stores `rtc.year` directly via `PUTBCD`, so the full year is reduced by decimal digit operations into the two BCD year digits.
- The diagnostic message on unstable reads is informal in the original source.
