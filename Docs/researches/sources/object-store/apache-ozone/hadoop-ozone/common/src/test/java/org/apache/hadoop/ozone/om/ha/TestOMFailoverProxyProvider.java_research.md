# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/ha/TestOMFailoverProxyProvider.java

Purpose: verifies core Hadoop RPC OM failover provider behavior for retry wait timing, proxy ordering, listener-node exclusion, and delegation-token service names.

Important APIs/types/functions: covers `HadoopRpcOMFailoverProxyProvider`, `selectNextOmProxy`, `performFailover`, `setNextOmProxy`, `getWaitTime`, `getOMProxyMap`, `OMProxyInfo.OrderedMap`, and `getCurrentProxyDelegationToken`.

Control flow and state: setup creates a three-node OM HA config. Tests alternate between failover to next nodes and same-node failover, verifying wait time resets or increases by `ozone.client.wait.between.retries.millis`. Listener nodes configured through `OZONE_OM_LISTENER_NODES_KEY` are omitted from the active proxy map.

Dependencies and integration points: uses `OzoneConfiguration`, `ConfUtils`, OM config keys, `UserGroupInformation`, and Hadoop `Text` token service names. The ordered map test shuffles input lists to prove iteration order follows constructor list order.

Risks and test signals: catches retry backoff regressions, inclusion of listener OMs in write/read proxy sets, unstable token service strings, and unordered proxy maps that could destabilize failover behavior.
