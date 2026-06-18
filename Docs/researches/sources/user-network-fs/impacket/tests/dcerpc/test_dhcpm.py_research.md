# sources/user-network-fs/impacket/tests/dcerpc/test_dhcpm.py

Purpose: tests DHCP Server Management Protocol request marshalling and helper functions for DHCP client and option lookup paths.

Important APIs and functions: `DHCPMTests` defines DHCPSRV v1/v2 UUIDs, `\PIPE\dhcpserver`, and packet privacy. Tests cover raw `DhcpGetClientInfoV4`, helper `hDhcpGetClientInfoV4`, raw `DhcpV4GetClientInfo`, `hDhcpEnumSubnetClientsV5`, and `hDhcpGetOptionValueV5`.

Control flow: v1 and v2 tests connect to specific interface UUIDs. Client-info calls build `DHCP_SEARCH_INFO_TYPE.DhcpClientName` searches for `serverName`. Option lookup derives the local subnet by replacing the target host octet with zero and asks for router option 3. Expected DHCP error codes are asserted with `assertRaisesRegex`.

State and persistence behavior: read-only. No DHCP scopes, clients, or options are changed.

Dependencies and integration points: uses endpoint mapper for TCP transport subclasses and skips SMB transports because Windows Server 2008 onward disables that path. It depends on DHCP service availability and `DCERPCTests` authentication.

Risks: success is often expected server-side failure (`ERROR_DHCP_JET_ERROR`, `ERROR_DHCP_INVALID_DHCP_CLIENT`, `ERROR_NO_MORE_ITEMS`, `ERROR_DHCP_SUBNET_NOT_PRESENT`), so different DHCP configuration can change outcomes. NDR64 option-value union handling is marked xfail for a known unimplemented case.

Test signals: proves DHCPM bindability, request union/discriminant encoding, helper parity, endpoint mapping, and expected error unmarshalling.
