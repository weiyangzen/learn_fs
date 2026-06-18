# sources/user-network-fs/impacket/tests/SMB_RPC/test_secretsdump.py

## Purpose

`test_secretsdump.py` covers both local parsing edge cases for SAM supplemental credentials and remote end-to-end smoke tests for the `impacket.examples.secretsdump` workflow. It embeds a trimmed `DumpSecrets` driver modeled after the example tool so tests can run VSS, SAM/LSA, and DRSUAPI extraction paths from code.

## Important APIs, Types, and Functions

`DumpSecrets` coordinates `SMBConnection`, `LocalOperations`, `RemoteOperations`, `SAMHashes`, `LSASecrets`, and `NTDSHashes`. It supports password, hashes, Kerberos, AES128, VSS, DRSUAPI-only, single-user, history, output file, resume file, and execution-method options through the `Options` class.

`NTDSHashesUnitTests` directly exercises `samr.unpack_user_properties`, `samr.USER_PROPERTY`, and the private `NTDSHashes.__decryptSupplementalInfo` path by constructing an `NTDSHashes` instance with `object.__new__` and setting private attributes needed for decryption. `SecretsDumpTests` defines remote scenarios for VSS with history, DRSUAPI for one administrator account, and full DRSUAPI.

## Control Flow

`DumpSecrets.dump()` branches between local hive mode and remote mode. Local mode derives the boot key from a SYSTEM hive or supplied bootkey. Remote mode attempts SMB login, creates `RemoteOperations`, configures the execution method, optionally enables the registry, obtains the boot key, and checks LM hash policy. If SAM/LSA processing is allowed, it saves SAM and SECURITY hives, dumps SAM hashes, cached LSA hashes, and LSA secrets, and exports them when an output file is configured. It then chooses an NTDS source: VSS-saved NTDS, local NTDS file, or DRSUAPI remote extraction, constructs `NTDSHashes`, runs `dump()`, handles selected DRSUAPI errors, and always attempts cleanup.

The unit tests build binary supplemental-credential blobs to verify header-only handling, Reserved5 parsing, property-data slicing, padding exclusion, and explicit `struct.error` failures for missing Reserved5 or too-short fixed headers.

## State and Persistence Behavior

Remote tests can create substantial remote and local side effects through `RemoteOperations`, including registry service access, hive saves, NTDS retrieval, resume files, and cleanup calls. `DumpSecrets.cleanup()` calls `finish()` on remote operations and hash dumpers. KeyboardInterrupt handling can prompt about deleting resume-session files. Unit tests avoid normal constructors for `NTDSHashes`, manually populate private dictionaries/callbacks, and validate that no Kerberos keys or cleartext passwords are recorded for header-only supplemental credentials.

## Dependencies and Integration Points

The file integrates `secretsdump` example logic with SMB authentication, remote registry/VSS execution methods, SAMR supplemental credential parsing, SAM/LSA/NTDS hash extraction, and DRSUAPI replication. It relies on `RemoteTestCase` for configured domain-controller-like targets and credentials, and `pytest.mark.remote` for remote selection.

## Risks and Edge Cases

Remote secretsdump tests are high-impact and environment-sensitive. They require privileged credentials, a suitable domain controller or Windows target, working SMB/registry/DRSUAPI/VSS paths, and careful cleanup. Some methods are prefixed `aaaa_` rather than `test_`, so WMI/MMC VSS variants are present but not collected by normal unittest discovery. The wrapper logs many errors instead of failing immediately, so remote smoke tests may miss partial extraction failures unless logs are reviewed. The unit tests cover recently fragile blob boundary cases: Reserved5 must exist even when no credential properties are present, and declared lengths shorter than the fixed header must fail.

## Test Signals

Strong local signals are `unpack_user_properties` accepting valid header-only/property blobs and rejecting malformed lengths. Remote signals are completion of VSS/history and DRSUAPI dump paths without unhandled exceptions and with cleanup. This file should be run after changes to `examples/secretsdump.py`, `samr.unpack_user_properties`, `NTDSHashes` supplemental credential parsing, remote registry operations, or DRSUAPI extraction.
