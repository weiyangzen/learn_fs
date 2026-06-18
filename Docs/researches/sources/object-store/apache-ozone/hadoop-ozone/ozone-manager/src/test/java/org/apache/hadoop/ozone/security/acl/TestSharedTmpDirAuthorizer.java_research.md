<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestSharedTmpDirAuthorizer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestSharedTmpDirAuthorizer.java

Purpose: verifies dispatch behavior of `SharedTmpDirAuthorizer`, ensuring shared tmp bucket paths use the native authorizer while other paths use the configured delegate authorizer.

Important APIs and functions: static `setUp`, `ozoneObjArgs`, and parameterized `testCheckAccess`.

Control flow: setup creates Mockito mocks for `OzoneNativeAuthorizer` and a mock third-party authorizer, then wraps them. The parameterized test builds a key `OzoneObjInfo` for four volume/bucket combinations and calls `checkAccess`. It verifies `nativeAuthorizer.checkAccess` only for `volume=tmp,bucket=tmp`; all other combinations verify delegate `authorizer.checkAccess`.

State and persistence behavior: no persisted state; only mock invocation history. The static shared authorizer is reused across parameter rows, so Mockito call accumulation is a minor maintenance risk if verification becomes stricter.

Dependencies and integration: `SharedTmpDirAuthorizer`, `OzoneObjInfo`, `RequestContext`, Mockito, JUnit parameterization. Risks include hard-coded tmp volume/bucket matching and lack of assertion on returned boolean. Test signal is routing, not authorization result semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestSharedTmpDirAuthorizer.java -->
