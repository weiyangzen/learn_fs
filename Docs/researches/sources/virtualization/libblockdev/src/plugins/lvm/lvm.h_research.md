# File Research: sources/virtualization/libblockdev/src/plugins/lvm/lvm.h

## Role
Public header for the LVM plugin ABI. It declares the LVM error domain, technology/mode enums, data structs returned to callers, ownership helpers, and all public plugin entry points.

## Public Data Model
- `BDLVMPVdata`: PV identity, free/total size, PE start, containing VG information, tags, and missing-state flag.
- `BDLVMVGdata`: VG name/UUID, size/free space, extent metrics, PV count, exported flag, and tags.
- `BDLVMSEGdata`: one LV segment's PE size, PV start PE, and backing PV device path.
- `BDLVMLVdata`: LV identity, size, attributes, segment type, origin/pool/data/metadata LVs, role/move information, progress percentages, tags, sub-LV arrays, metadata sub-LVs, and physical segment array.
- `BDLVMVDOPooldata`: VDO operating mode, compression/index/write-policy states, used size, saving percentage, index memory size, compression flag, and deduplication flag.
- `BDLVMVDOStats`: normalized VDO block usage, logical usage, used/saving percentages, and write amplification.
- `BDLVMCacheStats`: cache block/metadata sizing and usage, hit/miss counters, and cache mode.

## Public Enums
- `BDLVMError` covers dependency absence, command failure, parse errors, missing objects, DM errors, root/permission issues, cache errors, unsupported operations, VDO policy errors, and disabled devices.
- Cache pool flags describe data and metadata LV RAID/striped layouts.
- Cache, VDO operating, VDO compression, VDO index, and VDO write-policy enums provide typed API values over LVM string state.
- `BDLVMTech` and `BDLVMTechMode` define feature availability queries for basic LVM, snapshots, thin provisioning, cache, calculations, global config, VDO, writecache, devices-file support, shared VGs, config queries, and VG config backup/restore.

## API Surface
The header declares:
- plugin lifecycle and technology availability;
- PE/thin/cache calculation helpers;
- PV/VG/LV CRUD and query functions;
- tag management;
- lockspace start/stop for shared VGs;
- VG config backup/restore declarations;
- thin-pool and thin-snapshot functions;
- global config and devices filter functions;
- cache and writecache helpers;
- VDO pool/LV operations, enum string conversion, VDO stats, and VDO stats-full hash table query;
- LVM devices-file add/delete;
- `lvmconfig` query wrapper.

## Implementation Note
Not every declaration in this header is implemented in `lvm.c`; several helpers are provided by other LVM plugin source files not in this group. This header is the aggregate public ABI for the whole LVM plugin.
