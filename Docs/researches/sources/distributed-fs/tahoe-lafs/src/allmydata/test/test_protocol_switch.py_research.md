# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_protocol_switch.py

## Purpose
Unit-tests `_PretendToBeNegotiation`, a protocol-switch metaclass that makes classes treat Foolscap `Negotiation` instances as compatible for `isinstance` checks.

## APIs / Types / Functions
- `_PretendToBeNegotiation` is the metaclass under test.
- `foolscap.negotiate.Negotiation` is the compatibility target.
- `UtilityTests.test_metaclass` defines local `Parent`, `Child`, and `Other` classes.

## Control Flow
The test asserts normal instances satisfy normal class/subclass checks, real `Negotiation()` instances are considered instances of both metaclass-backed parent and child classes, and unrelated objects are not.

## State And Persistence
Only runtime type/metaclass state is involved.

## Dependencies / Integration Points
Sits at the boundary between Tahoe protocol-switch code and Foolscap negotiation. The file notes broader behavior is covered by end-to-end Foolscap tests and `test_istorageserver.py`.

## Risks And Test Signals
Only `isinstance` is covered, not real negotiation flow. Passing tests show Tahoe's compatibility shim preserves normal instance behavior while recognizing Foolscap negotiations.
