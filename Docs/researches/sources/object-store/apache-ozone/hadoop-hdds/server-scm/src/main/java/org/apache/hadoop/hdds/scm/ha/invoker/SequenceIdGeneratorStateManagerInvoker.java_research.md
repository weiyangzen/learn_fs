# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/SequenceIdGeneratorStateManagerInvoker.java

Purpose: Generated HA invoker for `SequenceIdGenerator.StateManager`, replicating sequence-id batch allocation.

Important APIs and types: `ReplicateMethod` includes `allocateBatch(String, Long, Long)`. Proxy methods replicate allocation and locally delegate `getLastId` and `reinitialize`.

Control flow: `allocateBatch` builds a direct Ratis request with sequence id name, expected last id, and new last id. On apply, `invokeLocal` calls the real state manager and encodes the Boolean CAS result.

State and persistence behavior: Persistent sequence-id table updates occur in the underlying state manager through the DB transaction buffer. Local cache reads and table reinitialization are not replicated.

Dependencies and integration points: Used by `SequenceIdGenerator.StateManagerImpl.Builder`; relies on string and long codecs and `RequestType.SEQUENCE_ID` registration.

Risks and test signals: CAS result correctness is central to monotonic id allocation. Tests should cover successful allocation, failed expected-last-id allocation, local last-id read, reinitialize table swap, and null/invalid sequence-id name handling.
