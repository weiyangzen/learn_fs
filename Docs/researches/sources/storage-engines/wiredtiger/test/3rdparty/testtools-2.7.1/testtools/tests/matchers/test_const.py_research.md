# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/matchers/test_const.py

## Purpose
This small module validates constant matchers: `Always` and `Never`.

## Important APIs, types, and functions
`TestAlwaysInterface` verifies that `Always()` matches arbitrary objects and has no mismatch descriptions. `TestNeverInterface` verifies that `Never()` rejects arbitrary objects and reports `Inevitable mismatch on <value>`.

## Control flow
Both classes use `TestMatchersInterface`, so examples are tested for match results, string output, descriptions, and details contract.

## State and persistence behavior
No state is persisted. The tested objects include integers, object instances, and strings.

## Dependencies and integration points
It depends on top-level `testtools.matchers.Always` and `Never`, plus the shared matcher interface helper. It is part of the matcher suite aggregator.

## Risks and test signals
Risk is low, but the tests lock down exact `__str__` and `Never` mismatch text. These are useful sentinel tests for matchers that intentionally ignore matchee structure.
