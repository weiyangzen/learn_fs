# sources/storage-engines/foundationdb/fdbrpc/IPAllowList.cpp

`IPAllowList.cpp` parses trusted IPv4/IPv6 CIDR subnets and supports peer-IP authorization checks for trusted fdbrpc endpoints.

`AuthAllowedSubnet` stores a normalized base address and address mask. `fromString()` parses `address/prefix` syntax with Boost.Asio, creates a byte mask through `createBitMask()`, normalizes the base address, and returns the subnet. `netmask()`, `netmaskWeight()`, and `printIP()` expose derived values. Test helpers generate random subnets/addresses and call `subnetAssert()` for diagnostics.

Control flow for parsing is split, parse address, compute mask, mask the base, and construct. Membership itself is provided by the allow-list/subnet operators declared in the header and tested here. The test covers fixed examples, all-address `/0`, exact-host `/32` and `/128`, family mismatch rejection, and randomized inclusion/exclusion.

State is in-memory in `IPAllowList` subnet vectors. `FlowTransport` copies an optional allow-list into `TransportData` and combines it with `IConnection::hasTrustedPeer()` before allowing private endpoint delivery.

Dependencies include Boost.Asio, fmt, bitset, `flow/UnitTest`, `flow/Error`, deterministic random, and `fdbrpc/IPAllowList.h`. Risks include malformed input exceptions, implicit prefix-width validation, cross-family mistakes, and security impact from overly broad trusted subnets. The direct test signal is `/fdbrpc/allow_list`.
