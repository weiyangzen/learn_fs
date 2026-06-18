## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/JavaUtils.java

Purpose: tiny utility for comparing the running Java specification major version. Important APIs: `isJavaVersionAtLeast(int)` and `isJavaVersionAtMost(int)`.

Control flow: static initialization reads `java.specification.version`, splits at `.`, parses the first component, and clamps to at least 8 so old `"1.8"` reports as 8. State/persistence: immutable static integer only.

Dependencies: Java system properties. Integration points: compatibility gates that need Java-version-specific behavior. Risks: versions with non-numeric prefixes would fail class initialization; the clamp means `isJavaVersionAtLeast(8)` is always true and versions below Java 8 are not distinguishable. Test signals: property-format tests for `"1.8"`, `"9"`, `"10"`, and current JVM; users should not rely on dynamic property changes after class load.
