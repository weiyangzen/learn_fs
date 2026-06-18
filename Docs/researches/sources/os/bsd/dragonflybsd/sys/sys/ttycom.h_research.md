# File Research: sources/os/bsd/dragonflybsd/sys/sys/ttycom.h

## Summary
User/kernel tty ioctl ABI definitions.

## Main Responsibilities
- Defines `struct winsize`.
- Defines modem-control bits and tty ioctl numbers for termios, line discipline, pgrp/session, pty packet mode, window size, break/DTR, draining, timestamps, and console/control tty behavior.
- Defines tty line discipline numbers.

## Important Behavior
The ioctl numbers preserve old BSD tty ABI allocation, including compatibility gaps. Pty packet-mode constants encode control events such as flush, stop/start, ioctl changes, and flow-control mode changes.

## Risks
This is a stable ABI header. Renumbering or changing structure layout would break userland utilities, pty consumers, terminal emulators, and compatibility layers.
