# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/matchers/test_higherorder.py

## Purpose
This module tests matchers that compose, transform, annotate, negate, or parameterize other matchers.

## Important APIs, types, and functions
It covers `AllMatch`, `AnyMatch`, `AfterPreprocessing`, `MatchesAny`, `MatchesAll`, `Annotate`, `AnnotatedMismatch`, `Not`, `MatchesPredicate`, and `MatchesPredicateWithParams`. Helper predicates `is_even()` and `between()` are used for predicate matcher tests.

## Control flow
Interface tests define example collections and expected descriptions for composed matchers. `AllMatch` accumulates all failed element descriptions; `AnyMatch` accumulates failed attempts when nothing matches. `AfterPreprocessing` transforms matchees before matching and optionally annotates descriptions. `MatchesAll` can report all mismatches or only the first. `Annotate.if_message()` either returns the original matcher or wraps it. Predicate-with-params returns a configured matcher factory.

## State and persistence behavior
No persistent state exists. Iterators are included among examples to verify one-pass iterable behavior.

## Dependencies and integration points
It depends on basic matchers, `Mismatch`, datastructure matchers, higher-order matcher implementations, shared helpers, and `FullStackRunTest`. These matchers are core building blocks for much of testtools' assertion vocabulary.

## Risks and test signals
Risks include exhausting iterators, losing mismatch details through annotation, unstable function reprs in `__str__`, and unexpected aggregation order. Tests check exact multiline descriptions and that `AnnotatedMismatch` forwards details.
