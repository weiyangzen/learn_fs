<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/AccountNameSpace.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/AccountNameSpace.java

## Purpose

`AccountNameSpace` defines the account-side isolation boundary for an Ozone tenant: account namespace ID, aggregate space usage, and quota settings.

## Important APIs, Types, And Functions

The interface declares `getAccountNameSpaceID`, `getSpaceUsage`, `setQuota`, and `getQuota`. It is annotated as limited-private and evolving.

## Control Flow, State, And Persistence

The interface contains no implementation. Implementations decide how usage and quota are calculated or enforced; comments allow lazy Recon aggregation or direct enforcement.

## Dependencies And Integration Points

It depends on `OzoneQuota`, `SpaceUsageSource`, and HDDS audience/stability annotations. It is used by the tenant abstraction and `AccountNameSpaceImpl`.

## Risks And Test Signals

The contract is broad and leaves enforcement semantics unspecified. Implementation tests should cover quota set/get, usage aggregation behavior, tenant isolation, and access ID naming conventions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/multitenant/AccountNameSpace.java -->
