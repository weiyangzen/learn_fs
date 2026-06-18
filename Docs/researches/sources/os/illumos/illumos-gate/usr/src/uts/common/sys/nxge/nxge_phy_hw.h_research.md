# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_phy_hw.h

## Purpose

`nxge_phy_hw.h` is the NXGE external PHY hardware catalog. It defines PHY IDs, MDIO clause types, port-address bases, device/register addresses, bitfield layouts, and small property structures for Broadcom, Marvell, Teranetics, NetLogic/AEL2020, SFP+, and QSFP PHY/module support.

## PHY Identification And Addressing

The header reserves ports 0 through 5 for on-chip SerDes and starts external PHY ports at `NXGE_EXT_PHY_PORT_ST`. It defines Clause 45 device addresses for PMA/PMD and PCS, standard ID register offsets, and chip IDs for Broadcom 8704/8706, Marvell 88X201x, Teranetics TN1010, and NetLogic/AEL2020.

Family ID masks intentionally ignore revision/model bits for Broadcom, TN1010, and NLP2020 devices. Address-base constants cover Neptune, N2, Goa, alternate Goa port 1, NLP2020 RF/QSFP port layouts, and Maramba variants.

## Broadcom 5464R And 8704/8706 Support

For BCM5464R, the file defines MII register numbers 16 through 30 and bitfield unions for:

- Extended control/status.
- RX error, false carrier, and RX-not-OK counters.
- Expansion register data/access.
- Auxiliary control/status.
- Interrupt status/mask.
- Shadow/miscellaneous access.
- Test register 1.

For BCM8704-class 10G PHYs, it defines PMD, PCS, PHYXS, and user-space register offsets, including control/status, IDs, speed ability, package devices, transmit disable, receive signal detect, XGXS lane status, analog/user controls, optics digital control, RX polarity, and alarm status. `phyxs_control_t`, `control_t`, `pmd_tx_control_t`, and `optics_dcntr_t` describe the important control words.

## Marvell, Teranetics, NetLogic, And Module Constants

Marvell 88X2011 definitions cover MMD addresses, PMA/PMD status, transmit disable, XGXS lane status, general control, LED blink/control fields, and helper macros for LED nibbles.

Teranetics TN1010 definitions cover PMA/PMD, PCS, PHYXS, autonegotiation, and vendor MMD1 registers. The file defines control bits for autoneg reset/enable/restart/link status, loopback modes, vendor autoneg status extraction, and speed extraction.

NetLogic/AEL2020 constants define PMA/PMD reset/link/signal-detect, optical setup, TX pre-emphasis, microcontroller control/start PC, PCS/PHYXS link/status/lane sync, GPIO module detect/action, and I2C snoop access to the transceiver.

SFP+/QSFP constants identify copper twinax and fiber connector types, QSFP MSA connector/length/low-power-mode registers, and a connector classification enum distinguishing fiber, copper shorter than 7m, and copper 7m or longer.

## Software Property Structures

`nxge_nlp_initseq_t` stores a PHY register/value initialization pair. `nxge_phy_mdio_val_t` stores device, register, and value triples. `nxge_phy_prop_t` wraps an array of MDIO triples with a count. These support device-property driven PHY tuning.

## Research Notes

The file contains no executable logic, but it centralizes hardware compatibility assumptions. Risk areas are mask correctness for PHY probing, MMD/device mismatch between PHY families, endian-sensitive bitfields, and duplicated/similar control typedef names for TN1010 PCS/PHYXS that can be confusing during maintenance.
