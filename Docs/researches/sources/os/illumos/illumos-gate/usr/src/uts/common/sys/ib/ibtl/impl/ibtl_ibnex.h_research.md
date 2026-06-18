# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl_ibnex.h

## Purpose

`impl/ibtl_ibnex.h` defines the private interface between IBTL and the InfiniBand nexus driver. It supports nexus callbacks, cfgadm client listing/unconfiguration data, HCA GUID/devinfo translation, verbose HCA data, parent validation, MPxIO pHCI registration, and HCA query by GUID.

## Main Interfaces

The header defines APID/string lengths, child names `ioc` and `ibport`, flags for `list_clients` and `unconfig_clients` style queries, callback argument data, and callback command values for IBC init/fini and reprobe requests.

The callback registration APIs allow IB nexus to provide a routine used by IBTL. Query APIs return packed NVL buffers for clients of a given HCA, translate HCA devinfo pointers to GUIDs and vice versa, collect verbose display data, validate client parents, register/unregister HCA devinfo as an MPxIO pHCI, and query HCA attributes plus driver identity/path.

## Research Notes

This is not a data-path header; it is device-tree and administration plumbing. It matters for hotplug, cfgadm, client unconfiguration, and multipath integration around IB HCAs and child devices.
