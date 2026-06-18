# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/ha/TestHadoopRpcOMFollowerReadFailoverProxyProvider.java

Purpose: tests follower-read behavior layered on top of `HadoopRpcOMFailoverProxyProvider` and Hadoop retry proxy mechanics.

Important APIs/types/functions: exercises `HadoopRpcOMFollowerReadFailoverProxyProvider`, `RetryProxy.create`, `getRetryPolicy`, `getProxy`, `getCurrentProxy`, `getLastProxy`, and `isUseFollowerRead`. It builds real `OMRequest` messages for `CreateKey` writes and `GetKeyInfo` reads.

Control flow and state: `setupProxyProvider` creates sorted mock OM proxies whose behavior is controlled by volatile flags in `OMAnswer`. Writes must route to the leader and leave the follower-read current proxy unchanged. Reads can use followers or leaders, fall back around unreachable followers, disable follower reads when followers report unsupported, and retry on `ReadIndexException` or `ReadException`.

Dependencies and integration points: uses Mockito, Hadoop `RetryInvocationHandler`, protobuf OM request/response types, Ratis read exceptions, and `RemoteException` wrapping for OM leader/follower errors. It also customizes proxy initialization to keep OM order deterministic.

Risks and test signals: protects against write requests accidentally sent to followers, follower-read mode sticking when unsupported, null/short invocation argument crashes, object methods selecting network proxies, and retry exhaustion when all OMs are unreachable. Threaded leader-ready tests verify retries wait until a leader becomes ready.
