# sources/storage-engines/foundationdb/flow/network.cpp

## Purpose
`network.cpp` implements Flow networking utility behavior shared by FoundationDB's simulation and real network layers. It covers chaos/fault metrics, disk/S3/bit-flip injector singletons, IP and network-address parsing/formatting, DNS-cache serialization, hostname-based connection setup, UDP socket destruction, starvation metric bins, and `NetworkInfo` TLS handshake lock ownership.

## Important APIs, Types, And Functions
Important entry points are `ChaosMetrics::clear`, `ChaosMetrics::getFields`, `DiskFailureInjector::injector`, `DiskFailureInjector::setDiskFailure`, `getStallDelay`, `getThrottleDelay`, `getDiskDelay`, `BitFlipper::flipper`, `S3FaultInjector::injector`, `IPAddress::parse`, `IPAddress::toString`, `IPAddress::isValid`, `NetworkAddress::parse`, `parseOptional`, `parseList`, `toString`, `formatIpPort`, `toIPVectorString`, `DNSCache::find/add/update/remove/clear/getKeys/getLastAccess/toString/parseFromString`, `INetworkConnections::connect(host, service, isTLS)`, `IUDPSocket::~IUDPSocket`, and the `NetworkInfo` constructor/destructor.

## Control Flow
Fault injector factories retrieve a process-global object from `g_network`, allocate it lazily when missing, and store it back under the appropriate `INetwork` global enum. Disk failure setup records stall/throttle windows from `g_network->now()`, derives a small deterministic stall duration, and emits a trace. Address parsing first strips `(fromHostname)` and `:tls`, then parses bracketed IPv6 `"[ip]:port"` through Boost.Asio or dotted IPv4 through `sscanf`; invalid formats throw `connection_string_invalid`. DNS cache parsing splits semicolon-separated host-service mappings and comma-separated address lists. Hostname connection first resolves endpoints asynchronously, chooses an address with `pickOneAddress`, marks it as hostname-derived, applies TLS flags, then connects with SNI when needed.

## State And Persistence
Chaos counters live in the `ChaosMetrics` object and are reset with `memset`, with `startTime` taken from the network clock. Disk/S3/bit-flip injectors are global network-scoped singletons. `DNSCache` persists an in-memory map keyed as `"host:service"` with address vectors and last-access timestamps; `toString` and `parseFromString` provide a compact textual representation. `NetworkInfo` owns a heap-allocated `FlowLock` sized by `FLOW_KNOBS->TLS_HANDSHAKE_LIMIT`.

## Dependencies And Integration Points
This file depends on Boost.Asio IP parsing, Flow `Arena`, `network.h`, UDP/socket/connection interfaces, `ChaosMetrics`, unit-test macros, `TraceEvent`, `deterministicRandom`, `FLOW_KNOBS`, and the global `g_network`. It integrates with connection-string parsing, DNS resolution, TLS hostname/SNI behavior, simulation fault injection, and Flow unit-test registration.

## Risks
IPv4 parsing uses signed `int` components and does not explicitly range-check octets or ports before composing the address, so malformed numeric strings outside normal ranges rely on downstream behavior. `DNSCache` serializes keys and addresses with comma/semicolon delimiters, making raw host/service values containing those delimiters unsafe. Injector factory methods assume `g_network` exists. `ChaosMetrics::clear` resets the whole object with `memset`, which is only safe while the type remains trivially resettable. Asynchronous hostname connection must preserve TLS/from-hostname flags so SNI is not lost.

## Test Signals
Embedded Flow tests cover DNS cache add/find/remove/clear, DNS cache string round trips including IPv6/TLS/fromHostname, IPv6 address parsing/compression, invalid IP strings, and IPv6 preference behavior depending on `RESOLVE_PREFER_IPV4_ADDR`. Additional useful signals are connection-string fuzzing, IPv4 range tests, TLS hostname connection tests, and simulation tests that verify disk delay and chaos metrics behavior.
