<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/upgrade/test/MockComponent.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/upgrade/test/MockComponent.java

Purpose: fixture component and annotated upgrade actions used to test HDDS upgrade action discovery/registration.

Important APIs/types/functions: `MockComponent`, no-op `mockMethodScm`, no-op `mockMethodDn`, nested `MockScmUpgradeAction`, nested `MockDnUpgradeAction`, `HDDSUpgradeAction<MockComponent>`, and `@UpgradeActionHdds` annotations bound to `INITIAL_VERSION`/`SCM` and `DATANODE_SCHEMA_V2`/`DATANODE`.

Control flow: executing each nested action calls the corresponding method on a supplied `MockComponent`. Tests use Mockito mocks of `MockComponent` to verify the call.

State and persistence behavior: no internal state or persistence. The class is purely a registration/execution fixture.

Dependencies and integration points: integrates annotation metadata with `HDDSLayoutVersionManager.registerUpgradeActions` scanning in the test package.

Risks: annotation values must stay aligned with feature/component expectations in the registration test. Since component methods are no-op, correctness depends on external verification.

Test signals: consumed by `TestHDDSLayoutVersionManager`, which validates discovery and method invocation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/upgrade/test/MockComponent.java -->
