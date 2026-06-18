# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/IPAllowList.h

## Purpose
`IPAllowList.h` declares subnet parsing and IP-address allow-list checks used to restrict trusted peers by IPv4 or IPv6 subnet.

## Important APIs, Types, and Functions
`AuthAllowedSubnet` stores a base address and address mask, constructs from strings, builds bit masks, matches `IPAddress` values through `operator()`, returns netmask/netmask weight, and has debug printing. `IPAllowList` stores subnet entries, exposes `addTrustedSubnet` overloads, `subnets`, and `operator()` for allow checks.

## Control Flow
Callers add trusted subnets as strings or parsed subnet objects. A check returns true for all addresses when the list is empty, otherwise it iterates subnets and returns true on the first match. IPv4 and IPv6 masks are kept separate; mismatched address families never match.

## State and Persistence Behavior
State is an in-memory vector of allowed subnets. There is no persistence, though callers may construct it from config files or command-line options.

## Dependencies and Integration Points
It depends on Flow `IPAddress`, `network.h`, and arena includes. `FlowTransport` accepts an `IPAllowList const*` during instance creation, making it part of transport authentication/trust decisions.

## Risks and Edge Cases
An empty allow list means allow all, which is convenient but security-sensitive. Correctness depends on robust `fromString` parsing and netmask validation in the implementation. Address-family mismatches are rejected, so dual-stack deployments need both IPv4 and IPv6 entries when appropriate.

## Test Signals
Tests should cover IPv4 and IPv6 CIDR parsing, boundary mask weights, empty-list allow-all behavior, nonmatching families, and multiple subnet ordering.
