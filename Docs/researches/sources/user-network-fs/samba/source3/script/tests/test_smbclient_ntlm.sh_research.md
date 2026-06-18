# sources/user-network-fs/samba/source3/script/tests/test_smbclient_ntlm.sh

## Purpose
This test validates NTLM and anonymous authentication behavior for `smbclient` over either NT1 or SMB3, including guest mapping and signing failure cases.

## Important APIs, Functions, and Control Flow
Inputs include server, username/password, `MAPTOGUEST`, `SMBCLIENT`, `PROTOCOL`, and config. The script rejects protocols other than `SMB3` or `NT1`. For NT1 it tests old-style no-SPNEGO/NTLMv1-compatible options and default NT1. For SMB3 it tests default SMB3. It covers valid username/password, anonymous no-password, anonymous bad-password with behavior depending on `MAPTOGUEST`, bad-user guest mapping, and signing-required failure paths for bad credentials.

## State, Dependencies, Integration, and Risks
No persistent state is created. Dependencies are the IPC share, server guest mapping policy, and auth options such as `clientusespnego`, `clientntlmv2auth`, and `--client-protection=sign`. Risks include broad output-only command checks and sensitivity to policy changes. Test signals are exit-status polarity through `testit` and `testit_expect_failure`.
