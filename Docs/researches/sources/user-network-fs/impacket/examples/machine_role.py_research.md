# sources/user-network-fs/impacket/examples/machine_role.py

## Purpose

`machine_role.py` queries MS-DSSP to retrieve a Windows host's machine role and primary domain details. It is intended as a lightweight pre-check for workflows that need to know whether a target is a workstation, member server, backup DC, or primary DC.

## Important APIs, Types, and Functions

`MachineRole.MACHINE_ROLES` maps `dssp.DSROLE_MACHINE_ROLE` enum values to human-readable labels. `MachineRole.__init__()` stores NTLM/Kerberos credentials, hashes, AES key, KDC host, and SMB port. `print_info(remoteName, remoteHost)` authenticates, fetches domain information, prints key/value output, and disconnects. `__get_transport()` builds an `ncacn_np:<remote>[\pipe\lsarpc]` transport and binds credentials/Kerberos settings. `__fetch()` calls `hDsRolerGetPrimaryDomainInformation()` and extracts role, NetBIOS domain, DNS domain, forest name, and GUID.

## Control Flow

The CLI parses target and connection/authentication options, prompts for a password when needed, forces Kerberos when `-aesKey` is supplied, defaults target IP to the parsed remote name, instantiates `MachineRole`, and prints fetched information. Authentication errors and fetch errors are logged as critical and exit with status 1.

## State and Persistence Behavior

The script is read-only and writes only stdout/log output. Runtime state is credentials and a transient DCE/RPC connection. No caches or local files are used.

## Dependencies and Integration Points

It depends on Impacket DCE/RPC transport, MS-DSSP helpers, UUID formatting, `parse_target()`, and the example logger. The endpoint is reached over SMB named pipe transport and uses either NTLM or Kerberos authentication.

## Risks and Edge Cases

The string binding uses `\pipe\lsarpc` while binding the DSSP UUID; this relies on the target exposing DSSP through that named pipe path. The role map assumes all returned enum values are known, so unexpected values raise `KeyError`. `__log_and_exit()` exits the process, limiting library reuse. Empty domain strings are allowed for local accounts. There is no explicit `finally` disconnect if printing raises after fetch.

## Test Signals

Tests should mock `hDsRolerGetPrimaryDomainInformation()` for every role enum, validate GUID formatting, and verify transport credential/Kerberos settings. Integration tests should run against standalone, member, and DC hosts on ports 139 and 445, with password, hashes, AES, and ccache-backed Kerberos.
