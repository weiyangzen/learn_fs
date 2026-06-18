# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/conf/TestReconfigurationHandler.java

## Purpose

This test class validates `ReconfigurationHandler` registration, listing, mutation, validation, unknown-property behavior, and admin-access checks for dynamically reconfigurable settings.

## Important APIs, Types, And Functions

The subject is built from `new ReconfigurationHandler("test", config, op -> adminCheck.get().accept(op))`, then registers two explicit setters and one annotated `SimpleConfiguration` object. Test constants cover explicit properties and generated keys `test.scm.client.compression.enabled` and `test.scm.client.wait`. `CheckedConsumer<String, IOException>` models accept/deny admin checks.

## Control Flow

Initialization registers property handlers before tests run. `getProperties()` and `listProperties()` compare exact sets/lists. `callsReconfigurationFunction()` updates atomic references and object-backed fields through `reconfigureProperty`. `validatesNewConfiguration()` rejects invalid wait time and confirms state preservation. `requiresAdminAccess()` swaps the admin checker to throw and verifies list/start/status calls propagate `IOException`.

## State And Persistence

State is per-test in-memory `OzoneConfiguration`, `AtomicReference` fields, and a mutable config object. No persistent store is used. Failed validation must leave object state unchanged.

## Dependencies And Integration Points

The class exercises HDDS config annotations, Hadoop `ReconfigurationException`, Ratis checked consumers, and the handler methods that are used by HTTP/admin reconfiguration endpoints.

## Risks

The exact expected property set is a compatibility guard; adding new annotated mutable properties requires updating the test intentionally. Unknown property behavior differs between `reconfigurePropertyImpl` and public `reconfigureProperty`, which callers must understand.

## Test Signals

Signals include exact property enumeration, successful setter callbacks, rejected invalid values, no throw for implementation-level unknown property, exception for public unknown property, and enforced admin checks on privileged methods.
