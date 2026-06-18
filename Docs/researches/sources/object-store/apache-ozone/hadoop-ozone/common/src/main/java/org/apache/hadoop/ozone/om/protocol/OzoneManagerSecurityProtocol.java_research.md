<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OzoneManagerSecurityProtocol.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OzoneManagerSecurityProtocol.java

## Purpose

`OzoneManagerSecurityProtocol` defines delegation token operations supported by OM.

## Important APIs, Types, And Functions

It declares `getDelegationToken(Text renewer)`, `renewDelegationToken(Token<OzoneTokenIdentifier>)`, and `cancelDelegationToken(Token<OzoneTokenIdentifier>)`.

## Control Flow, State, And Persistence

The interface has no implementation. Implementations issue, renew, and cancel tokens through OM security/token managers. Token state may be persisted or replicated by OM security infrastructure.

## Dependencies And Integration Points

It depends on Hadoop `Token`, `Text`, and Ozone token identifier classes. It is inherited by `OzoneManagerProtocol` and used by secure clients and delegation token selectors.

## Risks And Test Signals

Security behavior depends on authentication and token manager state. Tests should cover authorized issuance, renewer validation, renewal expiry, cancellation, invalid token handling, HA/failover behavior, and insecure cluster behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OzoneManagerSecurityProtocol.java -->
