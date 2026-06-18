# sources/user-network-fs/samba/source4/client/tests/test_smbclient.sh

## Purpose
Blackbox test script for Samba4 `smbclient`, covering share enumeration, common file operations, metadata queries, protocol compatibility, and credential source behavior.

## Important APIs, types, and functions
- Uses `testit` from `testprogs/blackbox/subunit.sh`.
- `runcmd()` executes `$smbclient //$SERVER/tmp -c "$cmd"` with config, domain, and credentials, then emits simple success/failure markers.
- Direct `testit` calls cover share listing and credential-source variants.

## Control flow
After argument parsing, the script lists shares authenticated and anonymously, copies the `smbclient` binary into `$PREFIX/tmpfile`, and uses it as test data. It runs `mput`, `altname`, `allinfo`, `mget`, `rm`, `mkdir`, `cd`, `rmdir`, nested directory creation/removal, `rename`, `deltree`, a series of `fsinfo` levels, `put`, `get`, `eainfo`, renamed put/get, SID/name lookup, LANMAN1/LANMAN2 listing, `pwd`, and several credential sourcing tests.

## State and persistence behavior
Creates and deletes files in `$PREFIX` and in the remote `tmp` share. It writes temporary authentication and password files under `$PREFIX`, exports `PASSWD_FILE`, `PASSWD`, and `USER` for parts of the run, then cleans the local files and restores variables.

## Dependencies and integration points
Requires a built `smbclient`, Samba selftest config, credentials, writable `tmp` share, old protocol support for LANMAN checks, and local `diff`. It directly exercises many handlers in `client.c`.

## Risks and edge cases
- `runcmd()` manually prints `test:`/`success:`/`failure:` rather than using `testit`, which may provide weaker subunit structure for those cases.
- It assumes old dialects and NTLM option combinations remain supported in the test environment.
- It does not validate command output content for metadata calls, only command success.
- Privilege tests are commented out, and ACL, UNIX extensions, recursion prompts, shell escape, and message mode are not covered.

## Test signals
Provides broad smoke coverage for normal `smbclient` workflows and credential plumbing. Failures here point at command dispatch, connection setup, transfer integrity, remote filesystem commands, or authentication regressions.
