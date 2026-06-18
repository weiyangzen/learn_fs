# File Research: sources/virtualization/spdk/lib/nvme/nvme_ns.c

This file owns NVMe namespace identify processing, namespace geometry/feature derivation, public namespace accessors, namespace identification descriptor parsing, command-set-specific identify data management, ANA accessors, and namespace clearing.

`nvme_ns_set_identify_data()` recalculates derived namespace state after Identify Namespace data changes. It marks identify complete, determines active state from nonzero NSID and nonzero NCAP, clears inactive namespaces, selects the active LBA format, computes sector size, extended LBA size, metadata size, max I/O sector counts, stripe boundary, namespace flags, PI type/format, and optional quirks such as MDTS excluding metadata and Intel striping. Controller identify capabilities determine deallocate, compare, flush, write zeroes, write uncorrectable, and reservation support.

The synchronous identify helpers allocate `nvme_completion_poll_status`, issue Identify commands through `nvme_ctrlr_cmd_identify()`, wait for admin completion, and install data on success. Separate helpers fetch base namespace data, ZNS-specific namespace data, NVM-specific namespace data when extended LBA format data is supported, KV-specific namespace data, and the namespace identification descriptor list. Descriptor-list retrieval is skipped for older controllers without IOCS support and for controllers with the Identify CNS quirk.

Public accessors expose NSID, active state, controller pointer, max transfer size, sector sizes, number of sectors, byte size, flags, PI type/format, metadata size, active format index, LBA format data, vendor-specific identify bytes, base identify data, NVM-specific identify data, deallocated-block read behavior, optimal I/O boundary, NGUID, UUID, CSI, ANA group ID, and ANA state. The deprecated format-index accessor logs a deprecation warning and delegates to the active-format helper.

Descriptor parsing walks the 4096-byte NS ID descriptor list using fixed four-byte descriptor headers and NIDL lengths. It returns null for zero-length terminators or malformed descriptors that overrun the buffer. UUID, NGUID, EUI64, and CSI descriptors are length-checked. NGUID and EUI64 descriptor values backfill Identify Namespace fields only when the identify fields are all zero; mismatches are logged and Identify Namespace values win.

Command-set-specific data is stored in a union pointer and freed through CSI-aware helpers. `nvme_ns_has_supported_iocs_specific_data()` returns true for ZNS and KV, and for NVM only when controller ELBAS is supported. Unsupported CSI values are logged and treated as unsupported.

`nvme_ns_identify()` performs the overall sequence: base Identify Namespace, inactive namespace shortcut, ID descriptor list, and supported IOCS-specific namespace data when multiple I/O command sets are enabled. `nvme_ns_clear()` zeroes identify data and descriptor list, frees IOCS-specific data, resets geometry, flags, CSI, active state, and identify-pending state.

Important invariants are that derived geometry must match active LBA format and metadata placement, descriptor values must not silently override nonzero Identify Namespace IDs, and IOCS-specific data lifetime must be cleared before replacing namespace state.
