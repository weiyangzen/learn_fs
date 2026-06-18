# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibnex/ibnex.h

This private IB nexus header defines child-node metadata, cfgadm/configuration states, reprobe coordination state, and global nexus instance state.

Core definitions:
- Internal return codes distinguish success, failure, offline failure, busy, and invalid node.
- IOC node data records IOU/IOC GUIDs, ID string, GID count, optional disconnected IOC profile, stringified IOC GUID, and PHCI GUID.
- Port node data records port number, communication-service index, port/HCA GUIDs, PKey, and parent dip.
- Pseudo-node data records node address, unit address/length, driver name, and merge-node flag.
- Node types include port, VPPA, HCA service, IOC, and pseudo nodes; HCA child mask groups port/VPPA/HCA service nodes.
- Node states track cfgadm configured/unconfigured/configuring/unconfiguring.
- Reprobe/AP flags track property-update notification behavior, always-notify behavior, IOC wait, and AP configured/unconfigured/configuring state.
- `ibnex_node_data_t` stores per-child devinfo private data plus typed node payload, list links, node type/state, reprobe state, and AP state.
- `ibnex_t` is the singleton IB nexus instance: dip, mutex, communication service name lists, child-node lists, NDI event handle/cookie, reprobe CV/state, disconnected IOC count, pseudo init flag, shared IOC list/CV/state, and taskq.
- Defines compatibility-name limits, enumeration source flags, node address size, GUID formatting, invalid PKey test, DDI event tag, and devtree status values.

Risk-sensitive invariants:
- Node type values are shared with the cfgadm IB plugin and must remain synchronized.
- Reprobe logic is designed to serialize reprobe-all with IOC-specific reprobes while allowing distinct IOC reprobes in parallel.
- Node payload structs are treated as stable read-only data after creation.
