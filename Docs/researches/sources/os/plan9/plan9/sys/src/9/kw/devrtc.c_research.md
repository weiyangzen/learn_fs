# File Research: sources/os/plan9/plan9/sys/src/9/kw/devrtc.c

## Purpose
Implements the Kirkwood real-time clock device `#r`, exposing a single `rtc` file containing seconds since 1970.

## Main Data Structures
- `RtcReg`: memory-mapped RTC time/date/alarm/interrupt registers.
- `Rtc`: decoded calendar fields.

## Behavior
- `rtcattach` maps `rtcreg` to `soc.rtc`.
- `rtcread` returns the current epoch seconds via `readnum`.
- `rtcwrite` accepts a numeric epoch value, converts it to calendar fields, and writes hardware registers.
- `rtctime` reads the RTC under interrupt lock until two consecutive reads match, reducing rollover inconsistency.
- `_rtctime` decodes BCD time/date registers, handling 12-hour and 24-hour modes.
- `setrtc` writes BCD fields back to hardware.
- `rtc2sec` and `sec2rtc` convert between calendar fields and seconds since 1970.

## Dependencies and Integration
Uses Plan 9 device helpers, `soc.rtc`, lock primitives, BCD conversion, and time constants.

## Risks and Notes
Leap-year logic treats every year divisible by 4 as leap, without century exceptions. Hardware year is decoded as 2000 plus a two-digit BCD value.
