# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/HddsWhiteboxTestUtils.java

Purpose: This test utility provides a small reflection-based replacement for Mockito/Hadoop Whitebox helpers whose availability changed across Hadoop versions. It lets tests read and write private fields portably.

Important APIs and types: Public methods are `getInternalState(Object, String)` and `setInternalState(Object, String, Object)`. Private helpers `getFieldFromHierarchy` and `getField` search the target class and superclasses for the named declared field.

Control flow: The utility starts from `target.getClass`, finds the requested field in the class hierarchy, calls `setAccessible(true)`, then gets or sets the value. Missing fields or reflection failures are wrapped in `RuntimeException` with diagnostic text.

State and persistence behavior: The utility owns no persistent state. It mutates arbitrary target object private fields when `setInternalState` is called.

Dependencies and integration points: It depends only on Java reflection and is used by tests that need to inspect or replace internal SCM state without relying on external Whitebox classes.

Risks: Reflection bypasses encapsulation and can make tests brittle across refactors. It does not handle static-field convenience explicitly, security-manager restrictions, module access restrictions, or primitive conversion beyond what `Field.set` supports. Error text says "set internal state" even for get failures.

Test signals: Tests using this helper should fail clearly when a field is renamed or moved outside the hierarchy. Direct tests could cover superclass lookup, get/set behavior, missing-field errors, and private field accessibility.
