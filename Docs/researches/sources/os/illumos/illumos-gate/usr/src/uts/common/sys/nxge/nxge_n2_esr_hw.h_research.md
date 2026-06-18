# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_n2_esr_hw.h

## Purpose

`nxge_n2_esr_hw.h` defines MDIO-visible register addresses and bitfields for the N2/NIU embedded SerDes blocks, covering two TI macro families: `WIZ6C2xxN2x0` and `WIZ7c2xxn5x1` / KT NIU. It is used by NXGE SerDes initialization and tuning code to program PLL, transmit, receive, status, and test registers.

## Register Map

The header defines `ESR_N2_DEV_ADDR` as device address `0x1e` and `ESR_N2_BASE` as `0x8000`. Register block offsets separate PLL, test, TX lanes, RX lanes, and a P1 block. Address macros compute low/high 16-bit MDIO words for:

- PLL config/status.
- Test config.
- TX config/status for channel `chan`.
- RX config/status for channel `chan`.

The macros use 4-word spacing per TX or RX lane and expose both combined and low/high register names.

## WIZ6C2xxN2x0 Definitions

The first register family defines:

- `esr_ti_cfgpll_l_t` for PLL enable, multiplier, and loop bandwidth.
- `esr_ti_cfgrx_l_t` / `esr_ti_cfgrx_h_t` for RX enable, test mode, bus width, rate, pair inversion, termination, alignment, loss-of-signal behavior, equalization, and clock-data recovery mode.
- `esr_ti_stsrx_l_t` for RX test failure, sync, odd code group, LOS detect, and BIST status.
- `esr_ti_cfgtx_l_t` / `esr_ti_cfgtx_h_t` for TX enable, test mode, bus width, rate, pair inversion, common mode, swing, de-emphasis, BIST, and FTP enable.
- `esr_ti_testcfg_t` for pattern tests, loopback, clock bypass, BIST enables, and rate.

Named constants enumerate PLL multipliers, RX CDR/equalization modes, TX swing/de-emphasis settings, bus widths, rates, terminations, alignment modes, and loopback modes.

## WIZ7 / KT / NIU Definitions

The KT-family definitions add wider PLL multipliers, `divclken`, clock bypass, PLL lock/divclk status, simplified test controls, expanded TX/RX bus-width fields, TX idle/sync/loopback/detect fields, and RX open-circuit/equalizer/loopback controls. The `K_` constants encode expected values for PLL enable, multipliers, RX/TX enable, rates, swing, de-emphasis, CDR, EQ, LOS, alignment, and loopback.

`nxge_serdes_prop_t` is a software property bundle for optional SerDes overrides: TX low/high, RX low/high, PLL low, and a bitmask saying which properties are set. The property bits are `NXGE_SRDS_TXCFGL`, `NXGE_SRDS_TXCFGH`, `NXGE_SRDS_RXCFGL`, `NXGE_SRDS_RXCFGH`, and `NXGE_SRDS_PLLCFGL`.

## Research Notes

This file is a pure ABI map for SerDes programming. The main risk is incorrect lane/channel arithmetic or applying constants from the wrong TI macro family. The `buswwidth` field spelling and `LOOOPBACK` constant spelling are historical API spellings that callers may depend on.
