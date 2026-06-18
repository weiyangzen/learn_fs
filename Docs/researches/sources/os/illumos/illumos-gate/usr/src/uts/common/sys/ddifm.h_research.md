# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddifm.h

This header defines the public kernel DDI fault-management interface for drivers. It includes DDI types and varargs support, and declares `ddi_system_fmcap`.

It defines FMA return statuses (`DDI_FM_OK`, fatal, nonfatal, unknown), driver capability flags for ereport generation, access-handle checking, DMA-handle checking, and error callbacks, plus convenience macros to test capabilities.

Error expectation values distinguish unexpected errors, expected errors, poke, and peek. Kernel-only `ddi_fm_error_t` carries structure version, status, expectation flag, ENA, optional access and DMA handles, bus-specific error data, and bus type. Bus types include default and PCI.

The file declares driver-facing FMA calls: `ddi_fm_ereport_post`, `ndi_fm_ereport_post`, `ddi_fm_service_impact`, handler register/unregister, `ddi_fm_init`, `ddi_fm_fini`, capability query, and access/DMA error get/clear calls.

Research notes:
- Drivers use this to harden device access and DMA paths and report service impact.
- Capabilities are negotiated through `ddi_fm_init` and can be influenced by system-wide FMA capability.
- Access/DMA error handling integrates with private caches in `ddifm_impl.h`.
