# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_mii.h

## Purpose

`nxge_mii.h` defines the NXGE driver's view of standard MII/GMII PHY registers and a small Broadcom-style shadow mode-control register. It is a hardware interface header: it exports register numbers, a compact register-index table, and 16-bit register union layouts with endian-aware bitfield ordering.

## Main Definitions

The register constants cover standard MII registers beyond the common `miiregs.h` set: link-partner next page, gigabit control/status, extended status, a vendor shadow register, and a mode-control shadow register. `NXGE_MAX_MII_REGS` fixes the PHY register index table at 32 slots.

`mii_regs_t` names the MII register indices as byte offsets: BMCR, BMSR, PHY IDs, autoneg advertisement/link partner/expansion/next page, gigabit control/status, extended status, vendor-reserved fields, and shadow registers.

The union definitions map the 16-bit register payloads:

- `mii_bmcr_t` for reset, loopback, speed select, autonegotiation, power-down, isolate, restart-autoneg, duplex, collision-test, and 1000-speed select.
- `mii_bmsr_t` for advertised link capabilities, extended status, preamble suppression, autoneg completion, remote fault, autoneg ability, link status, jabber, and extended capability.
- `mii_idr1_t` and `mii_idr2_t` for PHY OUI/model/revision identifiers.
- `mii_anar_t`, `mii_anlpar_t`, `mii_aner_t`, `mii_nptxr_t`, and `mii_lprxnpr_t` for autonegotiation base/next-page state.
- `mii_gcr_t` and `mii_gsr_t` for 1000Base-T master/slave, full/half duplex, local/remote receiver status, and idle error count.
- `mii_esr_t` for 1000X and 1000T extended capabilities.
- `mii_mode_control_stat_t` for a vendor shadow register that reports/controls copper/fiber mode, signal state, energy state, change indication, enable, and write-enable bits.

## Integration Notes

The header depends on `<sys/miiregs.h>` for base MII definitions and uses illumos `_BIT_FIELDS_HTOL` / `_BIT_FIELDS_LTOH` conventions. It has no functions and no storage. Consumers are expected to read/write MDIO registers as raw `uint16_t` values and interpret fields through these unions.

## Research Notes

The file is sensitive to hardware bit ordering, not control flow. Potential audit issues are register-layout drift, misuse of shadow-register write-enable semantics, and the typo-like formatting in `mii_lprxnpr_t`/`mii_esr_t`, though the bit widths themselves still add up to 16.
