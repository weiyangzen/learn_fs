# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerSubCommandUtil.java

## Purpose
Provides utility functions for DiskBalancer CLI commands, including datanode proxy creation and SCM-based target discovery.

## Important APIs, Types, And Functions
`getSingleNodeDiskBalancerProxy` parses host[:port] and creates `DiskBalancerProtocolClientSideTranslatorPB` with current user and `OzoneConfiguration`. `getAllOperableNodesClientRpcAddress` queries SCM for HEALTHY IN_SERVICE nodes and maps CLIENT_RPC addresses to display strings. `getDatanodeHostAndIp` formats a datanode protobuf into hostname/IP:port display text.

## Control Flow
Address parsing uses the default CLIENT_RPC port when no port is provided. Batch discovery iterates SCM nodes, extracts `DatanodeDetails`, skips DEAD nodes defensively, requires CLIENT_RPC port, and builds a deterministic `LinkedHashMap`.

## State And Persistence
No state is persisted. It creates network clients and reads SCM node metadata.

## Dependencies And Integration Points
Depends on `DiskBalancerProtocol`, `DiskBalancerProtocolClientSideTranslatorPB`, SCM query APIs, `DatanodeDetails.Port`, `NetUtils`, and `UserGroupInformation`.

## Risks And Test Signals
The simple `address.contains(":")` check is not IPv6-safe. Batch query already asks for HEALTHY but still checks DEAD. Tests should cover host-only default port, host:port, IPv6 or malformed addresses, missing CLIENT_RPC port, and hostname display formatting.
