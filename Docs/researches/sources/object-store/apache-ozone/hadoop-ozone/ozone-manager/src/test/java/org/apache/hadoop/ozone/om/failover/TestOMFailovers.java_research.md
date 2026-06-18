# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/failover/TestOMFailovers.java

Purpose: Tests OM failover retry behavior for `AccessControlException` through Hadoop RPC retry proxies.

Important APIs and types: `RetryProxy`, `HadoopRpcOMFailoverProxyProvider`, `OMFailoverProxyProviderBase`, `OMProxyInfo`, `OzoneManagerProtocolPB`, protobuf `OMResponse`, `ServiceException`, `AccessControlException`, and `GenericTestUtils.LogCapturer`.

Control flow: the test configures a mock failover provider with three OM proxy infos and proxies that always throw `ServiceException` wrapping the selected exception. It creates a retry proxy with default max attempts, calls `submitRequest`, expects a `ServiceException`, and checks debug logs mention all three OM node IDs.

State and persistence: no persistent state. Runtime state is failover proxy provider list, the selected test exception, and captured logs.

Dependencies and integration points: exercises client-side HA failover policy, proxy creation, node ordering, and logging behavior for permission-denied responses.

Risks and edge cases: Access-control failures might be treated as non-retryable or failoverable depending policy; this test asserts the current behavior tries every OM before surfacing the last access-control cause. Log-message format is part of the test signal and can be brittle.

Test signals: thrown `ServiceException` has `AccessControlException` cause and expected message prefix; captured logs contain retry debug lines for `om1`, `om2`, and `om3`.
