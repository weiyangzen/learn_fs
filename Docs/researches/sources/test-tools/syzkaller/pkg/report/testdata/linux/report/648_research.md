# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/648

## Purpose
This fixture validates lockdep parsing for `possible deadlock in tick_handler`.

## Important APIs, types, and functions
Important signals include `WARNING: possible circular locking dependency detected`, interrupt/tick handler context, lock dependency chains, and the expected `TYPE: LOCKDEP`.

## Control flow
The kernel emits a lockdep circular-dependency warning while handling timer tick activity. The parser should extract the canonical deadlock title from the lockdep report.

## State and persistence behavior
The fixture persists lock graph evidence and stack context only as static test data. No mutable state is modified.

## Dependencies and integration points
It exercises syzkaller's lockdep/deadlock recognizer, especially titles beginning `possible deadlock in ...`.

## Risks and test signals
The parser must classify the report as lockdep and keep `tick_handler` as the reported site rather than generic lockdep helpers.
