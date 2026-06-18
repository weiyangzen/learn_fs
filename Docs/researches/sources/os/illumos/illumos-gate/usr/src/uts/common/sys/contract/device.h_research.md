# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract/device.h

This header defines the device-contract public interface. It forward-declares device template and contract structures, defines device state transition events (`ONLINE`, `DEGRADED`, `OFFLINE`), accepted parameter bits, nonegotiable/minor terms, parameter operation constants, status field names, and default acknowledgement timeout.

It is layered on the generic contract ABI in `contract.h`.
