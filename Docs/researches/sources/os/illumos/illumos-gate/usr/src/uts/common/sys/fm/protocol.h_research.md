# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/protocol.h

This header defines the generic illumos Fault Management Architecture event protocol: common nvlist member names, class categories, FMRI schemes, event versions, ENA format helpers, and constructor prototypes.

Common event fields:
- Common names include `class` and `version`.
- Category classes include ereport, fault, defect, resource, list, and ireport.
- List event class names include suspect, isolated, repaired, updated, and resolved.

Ereport/list/fault/resource payload names:
- Ereports use detector and ENA.
- Ireports use detector, UUID, priority, and attributes.
- Suspect/list events use UUID, diagnosis code/time, diagnosis engine, fault list, status bits, injected marker, message, retire/response/severity.
- Fault events use ASRU, FRU, FRU label, certainty, resource, and location.
- Resource events use resource plus ASRU and transport-specific payload fields.

Status and version constants:
- Version constants are mostly `0`, with CPU scheme using version 1.
- Suspect status bits include faulty, unusable, not present, degraded, repaired, replaced, and acquitted.

ENA support:
- Defines format mask and formats 0, 1, 2.
- Defines bit masks and shifts for generation, id/cpuid, and time fields.
- Declares helpers to generate, increment, decode, and inspect ENAs.

FMRI scheme support:
- Common FMRI fields include authority, scheme, service authority, and facility.
- Authority fields include chassis id, product serial/id, domain, server, and host id.
- Schemes include fmd, dev, hc, svc, cpu, mem, mod, pkg, legacy-hc, zfs, sw, path, and pcie.
- Each scheme has version constants and member names for its specific fields, such as HC lists, device paths, package identifiers, service names, CPU cache data, memory unum/physaddr/offset, module package/name/id, ZFS pool/vdev, software object/site/context, path digraph, and PCIe list elements.

Constructors and utilities:
- Declares nvlist allocator helpers `fm_nva_xcreate`, `fm_nva_xdestroy`, `fm_nvlist_create`, and `fm_nvlist_destroy`.
- Declares setters for ereports, payloads, HC/dev/DE/CPU/mem/ZFS FMRIs, authority, and HC creation.

Dependencies and relationships:
- Includes kernel or userland nvpair headers depending on `_KERNEL`.
- This is the central naming and helper interface used by all specific FMA headers in this group.
