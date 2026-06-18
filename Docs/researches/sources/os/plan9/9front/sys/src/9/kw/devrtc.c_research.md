# File Research: sources/os/plan9/9front/sys/src/9/kw/devrtc.c

Implements the Kirkwood real-time clock device.

Key elements:
- Defines RTC register and decoded date/time structures.
- Converts between RTC date/time and seconds since 1970.
- Handles BCD decode/encode for hardware time/date registers.
- Reads the clock repeatedly until two consecutive samples match.
- Exposes `#r/rtc` as a numeric seconds file.
- Allows writing seconds to set the RTC.

Dependencies:
- Uses `soc.rtc` and Plan 9 device framework.

Research notes:
- Leap-year handling only checks divisibility by 4.
- The hardware stores years as `year % 100` offset from 2000.
