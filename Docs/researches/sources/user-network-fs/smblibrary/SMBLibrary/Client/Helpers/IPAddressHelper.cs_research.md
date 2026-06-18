<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/IPAddressHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/IPAddressHelper.cs

## Purpose
`IPAddressHelper` selects a preferred address from DNS results.

## Important APIs and Types
`SelectAddressPreferIPv4(IPAddress[] hostAddresses)` returns the first IPv4 address, or the first address if no IPv4 entry exists.

## Control Flow
The method scans the array for `AddressFamily.InterNetwork`; fallback is index zero.

## State, Dependencies, and Integration
The helper is stateless. `SMB1Client.Connect(string serverName, ...)` uses it after `Dns.GetHostAddresses()` so IPv4 is preferred for SMB transport.

## Risks and Test Signals
Empty arrays would throw, but `SMB1Client` checks for zero length before calling. Tests should cover IPv4-first, IPv6-only fallback, mixed IPv6/IPv4 ordering, and caller behavior for empty DNS results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/IPAddressHelper.cs -->
