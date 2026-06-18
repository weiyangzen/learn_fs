# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_sr_hw.h

## Purpose

`nxge_sr_hw.h` defines the Neptune SerDes register map and bitfields for RX/TX common control, reset, power, tuning, synchronization, test, and glue-control registers. It is a low-level MDIO/ESR hardware description for programming four SerDes lanes A through D across multiple ports.

## Register Addressing

The header defines Neptune ESR device/base constants and raw register offsets for common control, reset control, RX/TX power control, misc power control, per-lane RX/TX control, tuning, sync character, test, glue controls, and additional tuning banks. Address macros convert byte offsets into the PRM-required halfword register addresses by shifting right by one and adding low/high word selectors.

Per-lane macros compute low/high addresses from lane `chan` with `0x20` spacing. The address macros are used by driver code that reads/writes 16-bit SerDes registers.

## Bitfield Groups

The common control unions expose reference clock frequency, transmit-data master lane, termination/tuning fields, and reverse-loopback reference selection. Constants enumerate supported reference clock frequencies and master/reference lane selections.

Reset and power-control unions provide per-port/per-lane RX reset, TX reset, RX LOS powerdown, RX powerdown, TX PLL powerdown, TX powerdown, PECL/PLL/misc powerdown, and clock-output powerdown bits.

Per-lane RX/TX control and tuning unions define receive present window, rise/fall control, stretch enable, bias, FIFO/test controls, VMUX/VPULSE, RX equalization, TX level/termination tuning, sync character/mask/polarity, test reference/selftest fields, LOS test/enable, fast resync, samplerate, threshold count, bit-lock time, init time, receiver/transmitter termination, and trim enable.

## Constants

The file names values for RX present windows, bit-lock times, termination impedance settings, and initialization time windows. These constants are coupled to analog SerDes behavior rather than general software policy.

## Research Notes

This header has no functions and no state. Its main value is preserving hardware register semantics in a typed form. Risks are wrong low/high address calculations, applying lane macros to common registers, and changing bitfield definitions without matching the hardware PRM. The file uses explicit `#error` branches when neither bitfield ordering macro is defined.
