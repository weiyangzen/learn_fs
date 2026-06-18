<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/Tenant.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/Tenant.java

## Purpose

`Tenant` defines the high-level contract for Ozone tenant objects: name, account namespace, bucket namespace, access policies, and tenant roles.

## Important APIs, Types, And Functions

The interface declares getters plus mutators for adding/removing access policies and roles. It is limited-private and evolving.

## Control Flow, State, And Persistence

The interface has no implementation. Concrete classes decide how lists are stored and whether changes are persisted or only in memory.

## Dependencies And Integration Points

It depends on HDDS audience/stability annotations and the account/bucket namespace interfaces. `OzoneTenant` is the implementation in this subset.

## Risks And Test Signals

The API returns mutable `List<String>` in current implementation, so callers need clear ownership. Tests should cover tenant lifecycle code using this interface, policy/role mutation, and namespace coupling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/Tenant.java -->
