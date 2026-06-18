## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/annotation/InterfaceStability.java

Purpose: stability annotations for API compatibility expectations.

Important APIs/types: runtime-retained nested annotations `Stable`, `Evolving`, and `Unstable`. The class documentation defines how public and limited-private APIs should be paired with stability markings.

Control flow/state: no behavior beyond metadata. Dependencies: Java annotation APIs and `InterfaceAudience`.

Integration points: API compatibility policy, generated docs, and code review. Risks: annotations are advisory; incompatible changes are only prevented by process or tests. Runtime retention can affect reflection-based tooling. Test signals: source scanning or doc-lint style checks that public/limited-private classes are annotated.
