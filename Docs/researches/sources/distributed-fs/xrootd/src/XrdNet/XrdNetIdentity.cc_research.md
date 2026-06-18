## sources/distributed-fs/xrootd/src/XrdNet/XrdNetIdentity.cc

Purpose: Computes and exposes the process-wide network identity: fully qualified host name and domain suffix.

Important APIs and functions: Static initializer `getMyFQN`, `XrdNetIdentity::Domain`, `FQN`, and `SetFQN` are implemented.

Control flow: Initialization clears static buffers, honors `XRDNET_IDENTITY` if set, otherwise calls `gethostname`, lowercases it, enumerates interfaces, reverse-resolves public/private addresses, prefers names matching the short hostname, falls back to old DNS lookup, then public/private IP address, then bare hostname. `Domain` and `FQN` return static values and optional diagnostic text. `SetFQN` overrides identity and recalculates the domain pointer.

State and persistence: Static `DNS_FQN`, `DNS_Domain` pointer into `DNS_FQN`, `DNS_Error`, and `FQN_DNS` hold identity for the process. No persistence outside environment input.

Dependencies and integration points: Uses `XrdNetIF::GetIF`, `XrdNetAddr`, `XrdNetAddrInfo`, `XrdOucUtils`, `XrdOucTList`, `gethostname`, and `XrdSysE2T`. Used by `XrdNetAddr` default constructor and interface domain checks.

Risks: Static initialization performs network/interface discovery, which can be costly or order-sensitive. `XRDNET_IDENTITY` branch returns `false` even though identity was set, making `FQN_DNS` false by design. `SetFQN` does not lowercase input. Static buffers are not protected against concurrent `SetFQN` and reads.

Test signals: Environment override, lowercase conversion, hostnames with and without domain, matching public/private reverse DNS, DNS failure fallbacks, no usable interfaces, `SetFQN`, and `Domain` pointer correctness after changes.
