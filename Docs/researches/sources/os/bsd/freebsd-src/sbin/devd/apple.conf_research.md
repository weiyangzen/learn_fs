# File Research: sources/os/bsd/freebsd-src/sbin/devd/apple.conf

## Purpose
Defines PowerPC Apple-specific `devd` reactions.

## Main Elements
- PMU power button and lid close trigger `shutdown -p now`.
- Brightness keys adjust `dev.backlight.0.level`.
- Volume and mute keys call `mixer`.
- Eject key calls `camcontrol eject cd0`.
- PMU AC-line events invoke `service power_profile`.

## Dependencies And Integration
Installed only for `powerpc` by the Makefile. Relies on PMU event fields and userland utilities.
