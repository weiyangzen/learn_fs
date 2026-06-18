# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/__init__.py

## Purpose
`servers/__init__.py` exposes ntlmrelayx relay listener server classes from the package namespace. Importing it makes the configured server types available to the main ntlmrelayx orchestration code.

## Important APIs, Types, and Functions
The file imports `HTTPRelayServer`, `SMBRelayServer`, `WCFRelayServer`, `RAWRelayServer`, `RPCRelayServer`, `WinRMRelayServer`, `WinRMSRelayServer`, `RDPRelayServer`, and `MSSQLRelayServer`. It defines no classes or functions itself.

## Control Flow
Control flow is import-time only. Python resolves each server module and binds the class names into `impacket.examples.ntlmrelayx.servers`.

## State and Persistence Behavior
There is no runtime state beyond module imports and no persistence. Import failures in any listed server module can prevent the package from loading.

## Dependencies and Integration Points
This file couples the package namespace to all listed server implementations. It is an integration point for command-line server startup code that imports from `servers` rather than individual modules.

## Risks and Edge Cases
Eager imports mean optional dependencies of less common listeners, such as RDP TLS or MSSQL certificate generation dependencies, can affect package import if not handled in their modules. There is no `__all__`, so exported names are implicit.

## Test Signals
Test importing the package in environments with all server dependencies installed and with common listener selections. Static checks should catch stale class names when adding or removing server modules.
