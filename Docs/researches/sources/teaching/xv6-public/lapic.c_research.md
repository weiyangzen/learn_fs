# File Research: sources/teaching/xv6-public/lapic.c

Local APIC support plus CMOS RTC reading.

Key behavior:
- Defines LAPIC register indices and bit constants.
- `lapicinit` enables the local APIC, configures periodic timer interrupts, masks local lines, sets error vectors, clears errors, acknowledges pending interrupts, broadcasts INIT deassert, and enables interrupts at task-priority level.
- `lapicid` reads local APIC ID.
- `lapiceoi` acknowledges interrupts.
- `lapicstartap` programs CMOS warm reset vector and sends INIT/STARTUP IPIs to boot APs.
- `cmostime` reads CMOS RTC registers consistently and converts BCD values to binary year/month/day/time.

Notable details:
- `microdelay` is a stub.
- Timer calibration is hardcoded and intentionally approximate.
