<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantStateList.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantStateList.java

## Purpose

`TenantStateList` wraps a list of tenant state protobuf messages returned by tenant listing APIs.

## Important APIs, Types, And Functions

It exposes `getTenantStateList`, static `fromProtobuf`, `getProtobuf`, `toString`, `equals`, and `hashCode`. `getProtobuf` is deliberately not implemented and throws `NotImplementedException`.

## Control Flow, State, And Persistence

The class is a transient response wrapper. It stores the protobuf list directly and relies on upstream code to construct the list response. It does not persist or convert to a full list response.

## Dependencies And Integration Points

It depends on `TenantState` protobuf and Apache Commons `NotImplementedException`. It is returned by `OzoneManagerProtocol.listTenant`.

## Risks And Test Signals

Calling `getProtobuf` will fail. The list reference is stored directly. Tests should cover tenant listing response handling, equality for list content, no accidental call to `getProtobuf`, and mutation safety expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/TenantStateList.java -->
