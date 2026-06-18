<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/impl/AccountNameSpaceImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/impl/AccountNameSpaceImpl.java

## Purpose

`AccountNameSpaceImpl` is the simple concrete account namespace implementation for Ozone tenants.

## Important APIs, Types, And Functions

It implements `AccountNameSpace`, stores an account namespace ID, and implements `getAccountNameSpaceID`, `getSpaceUsage`, `setQuota`, and `getQuota`.

## Control Flow, State, And Persistence

Only the ID is stored. Usage and quota methods are placeholders returning null or doing nothing, so no quota or usage state is persisted by this implementation.

## Dependencies And Integration Points

It depends on `AccountNameSpace`, `OzoneQuota`, and `SpaceUsageSource`. It is constructed by `OzoneTenant`.

## Risks And Test Signals

Quota APIs are no-ops, which is important for callers expecting enforcement. Tests should assert current placeholder behavior, and future implementations should add quota set/get and usage aggregation coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/impl/AccountNameSpaceImpl.java -->
