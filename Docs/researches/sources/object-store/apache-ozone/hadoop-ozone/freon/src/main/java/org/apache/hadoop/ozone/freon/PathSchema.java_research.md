## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/PathSchema.java

Purpose: simple Freon path-name generator used by `BaseFreonGenerator.generateObjectName`.

Important APIs/types/functions: constructor stores a prefix; `getPath(long counter)` returns `prefix + "/" + counter`.

Control flow: no branching. Base Freon initializes one schema per command after prefix resolution.

State and persistence behavior: stores prefix. Generated names become persistent key/file paths in many Freon workloads.

Dependencies and integration points: used by `BaseFreonGenerator`.

Risks: empty prefix produces names like `/0`, which some commands intentionally allow but others avoid through random prefix generation; no zero-padding, so lexicographic order differs from numeric order.

Test signals: prefix and counter mapping should be deterministic.
