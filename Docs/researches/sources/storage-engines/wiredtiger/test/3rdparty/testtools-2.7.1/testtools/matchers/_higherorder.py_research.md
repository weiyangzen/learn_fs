# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/matchers/_higherorder.py

Purpose: matcher combinators and adapters that compose primitive matchers, invert them, annotate mismatches, preprocess values, or build predicate-based matchers.

Important APIs, types, and functions: `MatchesAny`, `MatchesAll`, `MismatchesAll`, `Not`, `MatchedUnexpectedly`, `Annotate`, `PostfixedMismatch`/`AnnotatedMismatch`, `PrefixedMismatch`, `AfterPreprocessing`, deprecated alias `AfterPreproccessing`, `AllMatch`, `AnyMatch`, `MatchesPredicate`, and `MatchesPredicateWithParams`.

Control flow: combinators call child matchers and aggregate or short-circuit according to semantics. `AfterPreprocessing` transforms the matchee before matching and optionally annotates the mismatch with transformation context. Predicate factories wrap boolean functions and format mismatch messages.

State and persistence: matcher instances store child matchers, predicates, options, and annotations. No external state unless caller-supplied preprocessors/predicates have side effects.

Dependencies and integration points: depends on `types` and core matcher/mismatch classes. This module is the composition layer used by most other matcher modules and `TestCase.assertThat`.

Risks and test signals: `MatchesAll` only consults `first_only` from `options` and ignores unknown keywords. Preprocessors can raise, causing assertion errors rather than mismatch objects. Test signals cover aggregation text, inversion behavior, annotations, predicate formatting, and alias compatibility.
