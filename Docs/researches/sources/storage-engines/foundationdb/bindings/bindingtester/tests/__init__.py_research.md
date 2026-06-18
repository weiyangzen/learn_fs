# sources/storage-engines/foundationdb/bindings/bindingtester/tests/__init__.py

## Purpose
This module defines the bindingtester test framework: result specifications, abstract test lifecycle hooks, instruction models, single-threaded and multi-threaded instruction containers, and dynamic import of concrete tests.

## Important APIs, Types, And Functions
`ResultSpecification` describes output subspace comparison, key slicing, ordering index, and global error filters. `Test` defines lifecycle methods (`setup`, `generate`, `pre_run`, result specs, expected results, validation) plus versionstamp encoding helpers and `create_test`. `Instruction` and `PushInstruction` encode operations with `fdb.tuple.pack`. `InstructionSet` is a list with stack/core bookkeeping and transactional insertion. `ThreadedInstructionSet` maps subspaces to instruction sets.

## Control Flow
`InstructionSet.insert_operations` chunks operation insertion into 5000-instruction transactions. `Test.create_test` finds a subclass whose module matches `bindingtester.tests.<name>`. `ThreadedInstructionSet` inserts each thread under its own subspace, substituting the caller-provided subspace for `None`.

## State And Persistence Behavior
Instruction insertion writes packed operation records into FoundationDB. In-memory framework state tracks core test boundaries for printing and per-thread instruction maps.

## Dependencies And Integration Points
It depends on FoundationDB tuple/subspace APIs, `bindingtester.util`, and concrete test modules imported by `util.import_subclasses`. `bindingtester.py` uses these classes to generate, insert, print, and validate tests.

## Risks And Edge Cases
`ThreadedInstructionSet.create_thread` raises a string instead of an exception object, which is invalid in Python 3 if triggered. `Test.create_test` assumes one subclass per module. Versionstamp encoding branches on API version 520 compatibility.

## Test Signals
Bindingtester print/run modes exercise instruction insertion, subclass discovery, and result spec filtering. No standalone unit tests are present.
