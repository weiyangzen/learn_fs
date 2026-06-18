<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/NetworkInterfaceHelper.cs -->
# sources/user-network-fs/smblibrary/SMBServer/NetworkInterfaceHelper.cs

## Purpose
Utility for the sample UI to enumerate local IPv4 addresses and find the subnet mask for a selected address.

## APIs, Types, and Functions
`GetHostIPAddresses()` returns a list of IPv4 `IPAddress` values from all network interfaces. `GetSubnetMask(IPAddress)` returns the matching `UnicastIPAddressInformation.IPv4Mask` or null.

## Control Flow, State, and Persistence
Both methods iterate `NetworkInterface.GetAllNetworkInterfaces()` and each interface's unicast addresses. No state or persistence.

## Dependencies and Integration
Used by `ServerUI_Load()` and NetBIOS name-server startup.

## Risks and Test Signals
Risks include including down/loopback/virtual interfaces, IPv4-only behavior, null subnet mask on some platforms, and no exception handling around network-interface APIs. Test multi-interface hosts, `IPAddress.Any`, disconnected adapters, and NetBIOS-over-TCP startup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/NetworkInterfaceHelper.cs -->
