## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/annotation/InterfaceAudience.java

Purpose: API audience annotations copied into the HDDS namespace to communicate public, limited-private, or private usage intent.

Important APIs/types: nested runtime-retained annotations `Public`, `LimitedPrivate(String[] value)`, and `Private`. The class itself is annotated public/evolving and has a private constructor.

Control flow/state: none at runtime besides Java annotation metadata. Dependencies: Java annotation APIs and `InterfaceStability`.

Integration points: source documentation, generated docs, static analysis, and compatibility review policy. Risks: runtime retention makes annotations visible via reflection; missing annotation on a public class is documented as private by default, which can surprise external users. Test signals: annotation retention and documentation generation rather than functional behavior.
