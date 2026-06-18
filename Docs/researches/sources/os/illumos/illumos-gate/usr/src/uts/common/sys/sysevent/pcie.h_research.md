# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent/pcie.h

## Purpose
Defines payload attribute names and detector flags for PCIe link-state sysevents.

## Main Interfaces
- `PCIE_EV_DETECTOR_PATH`: devfs path of detector node.
- `PCIE_EV_CHILD_PATH`: devfs path of updated child node.
- `PCIE_EV_DETECTOR_FLAGS`: PCIe change flags.
- Detector flags:
  - `PCIE_EV_DETECTOR_FLAGS_LBMS`
  - `PCIE_EV_DETECTOR_FLAGS_LABS`

## Dependencies And Relationships
Schema comments target `ESC_PCIE_LINK_STATE` events under `EC_PCIE`.

## Research Notes
This is a small schema header used to make PCIe link-change payloads self-describing and stable across producers/consumers.
