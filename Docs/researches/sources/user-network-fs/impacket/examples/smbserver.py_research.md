# sources/user-network-fs/impacket/examples/smbserver.py

## Purpose

`smbserver.py` starts a simple Impacket SMB server exposing one user-specified share. It can allow anonymous access, require a username/password or NTLM hashes, support SMB2, and optionally configure computer-account credentials for clients that require signing.

## Important APIs, Types, and Functions

The script is a single CLI entry point around `smbserver.SimpleSMBServer`. It calls `addShare()`, `setSMB2Support()`, `setDropSSP()`, `setKerberosSupport()`, `setNTLMSupport()`, `addCredential()`, `setComputerAccount()`, `setSMBChallenge()`, `setLogFile()`, and `start()`. Passwords are converted with `compute_lmhash()` and `compute_nthash()`.

## Control Flow

The CLI parses share name/path, optional auth, computer account signing options, listen address/port, IPv6, read-only mode, SMB2 support, NTLM/Kerberos toggles, drop-SSP, and output log file. It initializes logging, defaults the listen address, builds the server, adds the share, configures protocol/auth settings, validates mutually exclusive user versus computer-account auth, adds credentials if requested, sets an empty/default challenge, and starts the server until interrupted.

## State and Persistence Behavior

The process listens on the configured interface and port and exposes the provided filesystem path. It does not persist configuration outside memory. If `-outputfile` is used, server logs are written to that file. Shared files can be read or written by clients unless `-readonly` is set.

## Dependencies and Integration Points

It depends on Impacket `smbserver`, NTLM hash helpers, the example logger, local filesystem paths, and optional domain controller communication for computer account support.

## Risks and Edge Cases

Binding port 445 usually requires elevated privileges. Anonymous writable shares are possible by default if no username and no `-readonly` are set. Misconfigured computer-account options abort. The share path is trusted from the CLI and can expose sensitive local files. The fixed empty challenge delegates default behavior but users may expect explicit randomization.

## Test Signals

Tests should verify option validation, credential hash generation, anonymous versus authenticated configuration, read-only flag mapping, IPv4/IPv6 listen defaults, computer-account validation, and output log configuration. Integration tests should connect with SMB1/SMB2 clients and verify read/write/auth behavior.
