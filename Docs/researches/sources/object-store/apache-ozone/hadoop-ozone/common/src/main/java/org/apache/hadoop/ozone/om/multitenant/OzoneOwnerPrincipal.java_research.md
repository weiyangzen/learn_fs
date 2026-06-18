<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneOwnerPrincipal.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneOwnerPrincipal.java

## Purpose

`OzoneOwnerPrincipal` is a Java `Principal` representing the special Ozone owner identity.

## Important APIs, Types, And Functions

It implements `Principal`, has an empty constructor, `getName`, and `toString`. `toString` delegates to `getName`.

## Control Flow, State, And Persistence

The class is stateless and immutable. It is used as an identity token in authorization contexts rather than persisted metadata.

## Dependencies And Integration Points

It depends on `java.security.Principal`. It integrates with multitenant or Ranger policy code where owner-based principals are represented distinctly from users and roles.

## Risks And Test Signals

Because the name is constant, tests should verify exact principal name expected by policy code and serialization/display paths that call `toString`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/OzoneOwnerPrincipal.java -->
