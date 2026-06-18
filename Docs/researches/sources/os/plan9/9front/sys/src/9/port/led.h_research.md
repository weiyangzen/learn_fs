# File Research: sources/os/plan9/9front/sys/src/9/port/led.h

Common LED state definitions and helper prototypes.

Key contents:
- Defines `Ledport` with LED count, active LED state, and implementation-dependent LED bits.
- Defines IBPI-inspired LED states from `Ibpinone` through `Ibpifailarray`.
- Declares `ledname`, `name2led`, `ledr`, and `ledw`.

Role:
- Provides a small portable API for storage/enclosure-style LED state reporting.
