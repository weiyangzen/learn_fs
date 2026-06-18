<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneAuthorizerFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneAuthorizerFactory.java

Purpose: validates `OzoneAuthorizerFactory` class selection for OM and snapshot authorizers under ACL-disabled, native, third-party, and shared tmp-dir configurations.

Important APIs and functions: `aclsDisabled`, parameterized `nativeAuthorizer`, `thirdPartyAuthorizer`, parameterized `sharedTmpDirAuthorizer`, `assertSameInstanceForSnapshot`, `assertNewInstanceForSnapshot`, `configureOM`, `omMock`, and nested `MockNativeAuthorizer`/`MockThirdPartyAuthorizer`.

Control flow: tests build an `OzoneConfiguration`, mock an `OzoneManager`, set `OZONE_ACL_ENABLED`, `OZONE_ACL_AUTHORIZER_CLASS`, and optionally `OZONE_OM_ENABLE_OFS_SHARED_TMP_DIR`, then call `OzoneAuthorizerFactory.forOM`. Snapshot behavior is tested by stubbing `om.getAccessAuthorizer()` and calling `forSnapshot`.

State and persistence behavior: no persistence; all state is in mocked configuration and mocked OM getters. Snapshot behavior is the notable state rule: native authorizers get a new instance for snapshot access, while disabled and third-party authorizers reuse the OM instance.

Dependencies and integration: Ozone config keys, Mockito, JUnit parameter sources, `SharedTmpDirAuthorizer`, and factory code. Risks include factory behavior being sensitive to class inheritance from `OzoneNativeAuthorizer` and shared tmp-dir wrapping replacing a third-party authorizer when enabled. Test signal is type identity and instance identity assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneAuthorizerFactory.java -->
