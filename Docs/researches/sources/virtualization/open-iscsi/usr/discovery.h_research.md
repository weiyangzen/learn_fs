# File Research: sources/virtualization/open-iscsi/usr/discovery.h

Declares discovery entry points and forward declarations for discovery records, interface records, node records, and lists.

Exports:
- iSNS query/server-name helpers when `ISNS_SUPPORTED`.
- `discovery_fw`.
- `discovery_sendtargets`.
- `discovery_offload_sendtargets`.

It is the public interface for discovery implementations used by admin tools and daemon code.
