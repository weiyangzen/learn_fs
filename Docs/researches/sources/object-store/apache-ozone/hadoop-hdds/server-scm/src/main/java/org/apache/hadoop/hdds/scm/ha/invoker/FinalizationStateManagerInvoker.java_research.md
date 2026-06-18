# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/FinalizationStateManagerInvoker.java

Purpose: Generated invoker for SCM upgrade finalization state so finalization marks and layout-feature completion are replicated through Ratis.

Important APIs and types: Replicated methods are `addFinalizingMark`, `finalizeLayoutFeature(Integer)`, and `removeFinalizingMark`. Local methods include `crossedCheckpoint`, `getFinalizationCheckpoint`, `reinitialize`, and `setUpgradeContext`.

Control flow: Proxy replicated operations call `invokeReplicateDirect`; status/checkpoint queries and context updates call the local implementation. `invokeLocal` switches by method name, casts integer layout feature ids, and encodes boolean or checkpoint results.

State and persistence behavior: Underlying finalization state is stored in SCM metadata, especially the meta table and checkpoint markers. The invoker does not persist directly.

Dependencies and integration points: Used by SCM finalization manager and by `SCMHAManagerImpl.startServices` after DB reload.

Risks and test signals: Finalization is upgrade-sensitive; missing replication can split cluster layout state. Tests should cover all replicated mark transitions, checkpoint reads, reinitialize with new meta table, and exception translation.
