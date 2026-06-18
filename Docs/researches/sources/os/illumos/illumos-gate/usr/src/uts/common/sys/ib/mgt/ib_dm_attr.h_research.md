# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ib_dm_attr.h

## Purpose

`ib_dm_attr.h` defines InfiniBand Device Management attribute constants and wire-format structures from the IB specification’s device management section.

## Main Content

The header defines Device Management methods, class version, management status bits, and attribute IDs for class port info, notices, IO Unit Info, IOC controller profile, service entries, diagnostic timeout, prepare/test operations, and diagnostic code.

`ib_dm_io_unitinfo_t` describes an IO unit’s change ID, controller slot count, option ROM/diagnostic flags, and packed controller slot list. `ib_dm_ioc_ctrl_profile_t` describes an IOC controller profile with GUID, vendor/device IDs, subsystem IDs, I/O class/subclass, protocol/version, queue depths, message/RDMA sizes, control capability mask, service-entry count, reserved fields, and UTF-8 ID string. `ib_dm_srv_t` describes one service entry with UTF-8 service name and service ID.

## Constants

The file defines IO class values for vendor-specific, none, storage, network, video/multimedia, unknown/multiple, and subclass vendor-specific; controller capability mask values; controller service capability mask values; and service table limits.

## Research Notes

This header is management-plane metadata rather than transport data path. It is storage-relevant because it includes the IB Device Management I/O class value for storage controllers and the IOC service descriptors used to discover services exposed by IB I/O controllers.
