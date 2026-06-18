
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/IdentityProvider.java

## Purpose

`IdentityProvider` abstracts how a scheduler derives a caller identity from a `Schedulable`. This lets deployments choose whether scheduling groups by user, caller context, or another request attribute.

## Important APIs, types, and functions

The single method `makeIdentity(Schedulable obj)` returns a scheduling identity string or `null` if the provider cannot derive one.

## Control flow

`DecayRpcScheduler` calls providers when computing priority and recording cost. Its `getIdentity()` wrapper maps null to a fixed unknown identity for priority lookup.

## State and persistence behavior

The interface has no state. Implementations may be stateless or configuration-backed, but this file does not prescribe persistence.

## Dependencies and integration points

It depends on `Schedulable` and is configured through `CommonConfigurationKeys.IPC_IDENTITY_PROVIDER_KEY`. The default implementation in this package is `UserIdentityProvider`.

## Risks and test signals

Provider null handling must be consistent across all scheduler entry points. Tests should cover null identities, missing UGI, caller-context identities if implemented, and custom provider loading.
