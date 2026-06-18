# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/sa_recs.h

This header defines InfiniBand Subnet Administration record wire layouts from IB spec volume 1, release 1.1, chapter 15. It is a pure ABI/header definition file: no executable code, but many structs and component-mask constants used to form SA MAD queries and responses.

Key definitions:
- `ib_sa_hdr_t` is the SA MAD class header with `SM_KEY`, `AttributeOffset`, `Reserved`, and `ComponentMask`.
- Defines SA methods such as `SA_SUBN_ADM_GET`, `SA_SUBN_ADM_SET`, `SA_SUBN_ADM_GET_TABLE`, `SA_SUBN_ADM_GET_MULTI`, `SA_SUBN_ADM_DELETE`, and response variants.
- Defines SA MAD status codes and mask: `SA_STATUS_NO_ERROR`, resource/request/no-records/too-many-records/GID/component errors, and `SA_STATUS_ERROR_MASK`.
- Defines SA class port capability bits for optional records, UD multicast, multipath, and reinit support.
- Defines SA attribute IDs for ClassPortInfo, Notice, NodeRecord, PortInfoRecord, forwarding table records, SMInfo, ServiceRecord, PathRecord, MCMemberRecord, TraceRecord, MultiPathRecord, and ServiceAssociationRecord.

Record layouts:
- Topology and node data: `sa_node_record_t`, `sa_portinfo_record_t`, `sa_SLtoVLmapping_record_t`, `sa_switchinfo_record_t`, `sa_linearft_record_t`, `sa_randomft_record_t`, `sa_multicastft_record_t`, `sa_VLarb_table_record_t`, `sa_sminfo_record_t`, `sa_pkey_table_record_t`, `sa_guidinfo_record_t`, `sa_trace_record_t`.
- Subscription and service data: `sa_informinfo_record_t`, `sa_link_record_t`, `sa_service_record_t`, `sa_service_assn_record_t`.
- Pathing and multicast: `sa_path_record_t`, `sa_mcmember_record_t`, `sa_multipath_record_t`.

Layout/portability notes:
- Several records use endian-sensitive C bitfields guarded by `_BIT_FIELDS_HTOL` and `_BIT_FIELDS_LTOH`, inherited from `sys/isa_defs.h`.
- The file contains compile-time `#error` guards if no bitfield direction macro is defined.
- Component-mask constants map bit positions to every field in each SA record and are critical for SA queries.

Dependencies:
- Includes `sys/ib/ib_types.h` and `sys/ib/mgt/sm_attr.h`.
- Reuses SM attribute structures such as `sm_nodeinfo_t`, `sm_portinfo_t`, forwarding tables, P_Key tables, and GUID info.

Relevance:
- Important for InfiniBand fabric discovery and management, not directly filesystem-specific.
- In this subset it matters as OS/kernel storage-network substrate: InfiniBand/iSER and similar transports can support block/storage paths.
