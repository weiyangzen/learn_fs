# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListVolumesSecure.java

## Purpose
Secure-mode counterpart for list-volume authorization. It starts a Kerberos-backed standalone OM and verifies list-by-user and list-all behavior with ACL enabled and disabled, including OM admin principals from the configured host and another host.

## Important APIs, types, and functions
- Uses `MiniKdc`, Kerberos keytabs, `UserGroupInformation.loginUserFromKeytabAndReturnUGI`, and `doAs`.
- Starts `OzoneManager` directly with secure settings, `OMStorage`, test certificate/secret-key clients, and a testing SCM topology client.
- Uses `OzoneManagerProtocolClientSideTranslatorPB` over `OmTransportFactory.create` for direct OM protocol calls.
- Nested classes `AclEnabled` and `AclDisabled` start separate OM instances with different `OZONE_ACL_ENABLED` settings.

## Control flow
Global setup starts MiniKdc, creates admin/user principals and keytabs, configures Kerberos, and logs in UGIs. `startOM` creates a fresh metadata directory, initializes OM storage with a cert serial id, starts secure OM, creates six volumes with owners and optional ACLs, then closes the admin client. Nested tests toggle `om.getConfig().setListAllVolumesAllowed`, run checks under user/admin UGIs, and stop OM after each nested class.

## State and persistence behavior
Each nested mode writes a fresh OM metadata store containing volume ownership, ACL entries, default `s3v`, and secure VERSION/cert metadata. Authorization behavior depends on current UGI, ACL-enabled config, and runtime `listAllVolumesAllowed`.

## Dependencies and integration points
The test integrates Kerberos authentication, secure OM startup, native ACL authorizer, OM storage initialization, certificate and secret-key client test doubles, SCM topology client stubs, and direct protobuf client transport.

## Risks and edge cases
Secure setup is environment-sensitive because it uses canonical local host names and MiniKdc. `checkUser` closes the client in both try and finally paths, which relies on close idempotency. Admin principal matching intentionally covers another host, so admin short-name/host rules are part of the contract.

## Test signals
Signals include exact accessible volume sets for each UGI, successful or denied list-all according to ACL/list-all config, six explicitly created volumes plus `s3v` for admin expectations, and `PERMISSION_DENIED` classification for expected failures.
