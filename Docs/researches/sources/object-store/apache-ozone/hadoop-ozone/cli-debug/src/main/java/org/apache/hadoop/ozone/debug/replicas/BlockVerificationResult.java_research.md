# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/BlockVerificationResult.java

Purpose: `BlockVerificationResult` is the JSON-facing result model for one replica check.

Important APIs and types: It stores `completed`, `pass`, and `failures`, and offers factories `pass`, `failCheck`, and `failIncomplete`.

Control flow and state: Instances are immutable after construction. `failCheck` means the check completed and found bad data; `failIncomplete` means the verifier could not complete due to an operational error.

Dependencies and integration points: `ReplicasVerify` serializes these values into each replica's `checks` array and uses `passed()` to compute block/key pass state.

Risks: Failure lists are not defensively copied, though factories use immutable singleton/empty lists. There is no typed reason code beyond message text.

Test signals: Tests should assert factory semantics, getters, and serialization shape.
