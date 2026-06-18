<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/resolve_host.h -->
# sources/user-network-fs/cifs-utils/resolve_host.h

## Purpose

`resolve_host.h` declares the shared host resolver API and address-list size constants.

## Important APIs, Types, and Functions

It defines `MAX_ADDRESS_LEN` as `INET6_ADDRSTRLEN`, `MAX_ADDRESSES` as 16, `MAX_ADDR_LIST_LEN` as `(MAX_ADDRESS_LEN + 1) * MAX_ADDRESSES`, and declares `resolve_host`.

## Control Flow

Callers allocate a buffer of `MAX_ADDR_LIST_LEN`, call `resolve_host`, and receive a comma-separated list of address strings or an error code compatible with `mount.h`.

## State and Persistence Behavior

No state is defined. The caller owns the output buffer.

## Dependencies and Integration Points

It includes `<arpa/inet.h>` for address string sizes and is consumed by mount, credential, PAM, and key helpers.

## Risks and Edge Cases

`MAX_ADDRESS_LEN` does not include IPv6 scope-id suffix text, though `resolve_host.c` may append `%<scopeid>` into a larger temporary buffer before copying into the aggregate list. `MAX_ADDR_LIST_LEN` assumes one separator per address and no final NUL margin beyond the expression's arithmetic, so caller buffers should use exactly the macro.

## Test Signals

Compile tests and resolver integration tests should validate buffer sizing for IPv4, IPv6, scoped IPv6, and maximum address counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/resolve_host.h -->
