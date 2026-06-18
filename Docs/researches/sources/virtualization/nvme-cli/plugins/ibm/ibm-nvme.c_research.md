# File Research: sources/virtualization/nvme-cli/plugins/ibm/ibm-nvme.c

- Purpose: IBM vendor plugin for additional SMART log, VPD log, and IBM-specific persistent event log decoding.
- Additional SMART: reads vendor log `0xF0` into packed IBM attribute entries and prints known attributes such as read errors, retired blocks, power-on hours, power cycles, ECC, erased MB, spare blocks, program/erase failures, life remaining/used, temperature, thermal throttling, flash/host lifetime I/O, backup failures, security wear, and PCIe receive errors.
- VPD log: reads vendor log `0xF1` and prints fixed-width fields for part numbers, EC/FRU/final assembly, feature code, CCIN, 11S serial, SSID, endurance, capacity, warranty, encryption, RCTT, load ID, location, timeout values, queue count, media type, manufacturer serial, and firmware.
- Persistent events: retrieves standard persistent event log context, scans event entries for vendor-specific event type `0xDE`, then decodes IBM change-definition and reported-error vendor event payloads.
- Output modes: SMART and VPD support raw binary; persistent event supports binary and verbose human decoding through common PEL header helpers.
- Memory note: persistent event allocation uses `libnvme_alloc` but does not free `pevent_log_info` before return in this file.
