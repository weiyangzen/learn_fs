# sources/user-network-fs/impacket/impacket/dcerpc/v5/dhcpm.py

## Purpose
`dhcpm.py` implements Impacket's `[MS-DHCPM]` DHCP server management RPC bindings. It defines UUIDs, DHCP-specific error constants, NDR structures for DHCP clients, subnets, reservations, option scopes, option data, subnet elements, and call/response classes plus helper functions for common DHCP server enumeration and lookup operations.

## Important APIs, Types, and Functions
- Interface UUIDs are `MSRPC_UUID_DHCPSRV` for `dhcpsrv` and `MSRPC_UUID_DHCPSRV2` for `dhcpsrv2`.
- `DCERPCSessionError` formats DHCPM failures using generic Windows system errors plus module-local DHCP error messages.
- Core aliases include `DHCP_SRV_HANDLE`, `DHCP_IP_ADDRESS`, `DHCP_IP_MASK`, and `DHCP_OPTION_ID`.
- Enumerations include `DHCP_SEARCH_INFO_TYPE`, `QuarantineStatus`, `DHCP_SUBNET_STATE`, `DHCP_OPTION_SCOPE_TYPE`, `DHCP_SUBNET_ELEMENT_TYPE`, and `DHCP_OPTION_DATA_TYPE`.
- Client structures include `DHCP_CLIENT_INFO_V4`, `DHCP_CLIENT_INFO_V5`, `DHCP_CLIENT_INFO_VQ`, `DHCP_CLIENT_INFO_PB`, their pointer and array wrappers, `DHCP_SEARCH_INFO`, `DHCP_CLIENT_SEARCH_UNION`, `DHCP_BINARY_DATA`, `DHCP_CLIENT_UID`, and `DATE_TIME`.
- Subnet and option structures include `DHCP_SUBNET_INFO`, `DHCP_OPTION_SCOPE_INFO`, `DHCP_RESERVED_SCOPE`, `DHCP_BOOTP_IP_RANGE`, `DHCP_IP_RESERVATION_V4`, `DHCP_IP_RANGE`, `DHCP_IP_CLUSTER`, `DHCP_SUBNET_ELEMENT_DATA_V5`, `DHCP_OPTION_DATA_ELEMENT`, `DHCP_OPTION_DATA`, `DHCP_OPTION_VALUE`, `DHCP_OPTION_VALUE_ARRAY`, and `DHCP_ALL_OPTIONS_VALUES`.
- RPC call classes cover `DhcpGetSubnetInfo`, `DhcpEnumSubnets`, `DhcpGetOptionValue`, `DhcpEnumOptionValues`, `DhcpGetClientInfoV4`, `DhcpEnumSubnetClientsV4`, `DhcpEnumSubnetClientsV5`, `DhcpGetOptionValueV5`, `DhcpEnumOptionValuesV5`, `DhcpGetAllOptionValues`, `DhcpEnumSubnetElementsV5`, `DhcpEnumSubnetClientsVQ`, and `DhcpV4GetClientInfo`.
- `OPNUMS` maps opnums 0, 2, 3, 13, 14, 21, 22, 30, 34, 35, 38, 47, and 123 to request/response classes.
- Helper functions beginning with `h` build and submit common requests: `hDhcpGetClientInfoV4`, `hDhcpGetSubnetInfo`, option value helpers, subnet enumeration helpers, client enumeration helpers, and subnet element enumeration.

## Control Flow
Most of the file is declarative NDR schema. Callers bind a DCE/RPC connection to one of the DHCP server UUIDs and then either instantiate request classes directly or use the helper functions. Helpers populate the nullable `ServerIpAddress` with `NULL` to address the bound server, set discriminator fields for unions such as `SearchInfo.SearchInfo.tag` or `ScopeInfo.ScopeInfo.tag`, fill request-specific fields, then call `dce.request(request)`.

Search helpers choose the correct union arm based on `DHCP_SEARCH_INFO_TYPE`: client IP address, hardware address, or client name. Option helpers choose the correct scope union arm based on `DHCP_OPTION_SCOPE_TYPE`: default/global options have no union payload, subnet options use an IPv4 address, reserved options use `DHCP_RESERVED_SCOPE`, and multicast scope options use a wide string. Enumeration helpers initialize resume handles to `NULL`, set `PreferredMaximum`, submit the request, and return the first response or the exception packet when the server reports end-of-data style status that the helper expects.

## State and Persistence Behavior
The module itself keeps no mutable global state beyond constants and class definitions. Helper functions are stateless and do not persist resume handles between calls. Remote DHCP server state is read by all currently implemented helpers; the file defines structures and errors for mutable concepts such as scopes, ranges, clients, reservations, policies, options, and failover, but the provided helper surface is focused on lookup/enumeration. The returned packets can include server-side resume handles, but callers must manage pagination manually if they need to continue past a first partial response.

## Dependencies and Integration Points
The file depends on Impacket's NDR call, structure, pointer, array, enum, and union classes; DHCP uses `dtypes` primitives such as `LPWSTR`, `DWORD`, `LPDWORD`, `BOOL`, `BYTE`, and `WORD`. Error handling uses `system_errors` and `DCERPCException`. UUID generation uses `uuidtup_to_bin`. It integrates with the rest of Impacket through the standard DCE/RPC transport and request machinery: callers bind a transport to `MSRPC_UUID_DHCPSRV` or `MSRPC_UUID_DHCPSRV2`, and `OPNUMS` supports response decoding.

## Risks and Edge Cases
- The helper pagination loops return inside the first iteration, so they do not actually continue while `ERROR_MORE_DATA` or `STATUS_MORE_ENTRIES` is present. Callers expecting full enumeration must handle resume handles themselves.
- Several helpers catch exceptions by matching text such as `ERROR_NO_MORE_ITEMS` or `STATUS_MORE_ENTRIES`; changes in exception formatting can break this behavior.
- `hDhcpEnumSubnetClientsV5()` catches `DCERPCSessionError`, while many other helpers catch `DCERPCException`; inconsistent exception types can miss expected packets.
- Some NDR structures appear suspicious: `DHCP_BOOTP_IP_RANGE` defines `MaxBootpAllowed` twice with different types, causing the first field name to be overwritten in Python structure semantics.
- The `DhcpEnumSubnetClientsV5Response` class omits an explicit `ErrorCode` field unlike the nearby V4/VQ responses, which should be checked against the protocol and decoder behavior.
- Helper defaults often use `SubnetAddress = NULL` or `0`; callers need to know when the server treats this as all subnets versus an invalid scope.
- DHCP IP addresses are raw DWORDs, so callers must provide network/order values consistent with Impacket and protocol expectations.
- Memory ownership/freeing of server-allocated buffers is not modeled; the library relies on decoded response objects rather than explicit RPC free calls.
- The module exposes many DHCP error constants but only a small subset has custom human-readable messages.

## Test Signals
Useful tests should include:
- NDR encode/decode golden tests for each DHCP client info version, option data union arm, option scope union arm, subnet element union arm, and call/response class in `OPNUMS`.
- Unit tests for helper request construction, especially union `tag` values and payload fields for client search and option scope variants.
- Pagination/resume-handle tests with mock DCE responses that include `ERROR_MORE_DATA`, `STATUS_MORE_ENTRIES`, and no-more-items exceptions.
- Error formatting tests for generic `system_errors`, module-local DHCP errors, and unknown errors.
- Regression tests for suspicious structures such as duplicate `MaxBootpAllowed` and `DhcpEnumSubnetClientsV5Response` response shape.
- Integration tests against a Windows DHCP server for subnet enumeration, subnet info lookup, client enumeration across V4/V5/VQ variants, option value lookup, all option values, and subnet element enumeration.
