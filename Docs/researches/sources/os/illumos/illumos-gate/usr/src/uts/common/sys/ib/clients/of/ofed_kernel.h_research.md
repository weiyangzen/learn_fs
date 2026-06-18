# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/ofed_kernel.h

## Purpose

Collects Solaris OFED compatibility definitions imported from OpenIB headers, including MAD size constants, CM SIDR status values, and SA path record layout.

## Main Definitions

- License/comment block documents imported content from `ib_mad.h`, `ib_cm.h`, and `ib_sa.h` under OpenIB BSD terms.
- Includes Solaris OFA wrapper, OFED verbs, user verbs, and user MAD headers.
- MAD management header/data size enum:
  - General MAD, RMPP, vendor, SA, device, and SNMP header/data sizes.
- `enum ib_cm_sidr_status`: SIDR result codes for success, unsupported, reject, no QP, redirect, and unsupported version.
- `struct ib_sa_path_rec`: SA path record with service ID, DGID/SGID, LID fields, raw traffic, flow label, hop limit, traffic class, reversibility, number of paths, P_Key, QoS class, SL, MTU/rate/lifetime selectors and values, and preference.

## Integration Notes

This is a compatibility aggregation header for OFED-derived kernel interfaces in illumos. It bridges local Solaris headers with imported OFED user/kernel ABI definitions.

## Risks and Gotchas

- The imported definitions must remain ABI-compatible with the OFED consumers they emulate.
- `struct ib_sa_path_rec` uses OFED types from `ib_verbs.h`, including `union ib_gid`.
