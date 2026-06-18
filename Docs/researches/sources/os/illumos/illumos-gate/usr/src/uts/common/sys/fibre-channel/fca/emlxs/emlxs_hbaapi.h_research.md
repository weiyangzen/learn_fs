# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_hbaapi.h

Purpose: Carries the SNIA HBA API public header used by clients and libraries, with Emulex/RackTop-local copy adjustments for kernel/user builds.

Key definitions:
- `HBA_LIBVERSION` is 2.
- `HBA_API` handles Windows DLL import/export and is empty elsewhere.
- Platform typedefs define fixed HBA integer/pointer types for Windows and Unix/kernel use.
- `HBA_HANDLE`, `HBA_STATUS`, status constants, port type/state/speed constants, class-of-service type, FC-4 type bitmap, WWN, IP address, and boolean types.
- Adapter/port attribute structures: `HBA_ADAPTERATTRIBUTES`, `HBA_PORTATTRIBUTES`, `HBA_PORTSTATISTICS`.
- FCP mapping/binding structures: `HBA_SCSIID`, `HBA_FCPID`, `HBA_LUID`, `HBA_FCPSCSIENTRY`, V2 variants, target mapping, binding entries, and persistent binding structures.
- Management/event structures: WWN type, `HBA_MGMTINFO`, link/RSCN/proprietary event info, `HBA_EVENTINFO`, and optional userland `HBA_LIBRARYATTRIBUTES`.
- Binding capability/status/effective constants and FC-4 statistics.
- Event classes cover adapter, port, port-statistics, target, and fabric-link events.
- Function prototypes cover library load/free, adapter enumeration/open/close, adapter/port attributes, port statistics, discovered ports, CT passthrough, event buffers, RNID/RLS/RPL/RPS/SRL/LIRR, FC4/FCP statistics, refresh/reset, target mapping, persistent binding, SCSI inquiry/report LUNs/read capacity, callback registration/removal, and library attribute queries.

Dependencies and interactions:
- Used by driver/userland HBA management paths and DFC event structures referenced in `emlxs_events.h` and `emlxs_extern.h`.
- Guards `struct tm` and library attributes out of kernel builds with `_KERNEL`.

Implementation notes:
- This is an ABI/API header, so field widths and constants are compatibility-sensitive.
- Several comments preserve original SNIA naming and misspellings such as “Depricated” and “Persistant”.
- `HBA_ScsiInquiryV2` lacks `HBA_API` while adjacent exported prototypes include it; that may be intentional or legacy.
