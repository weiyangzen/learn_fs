# sources/security-integrity/selinux/python/sepolgen/tests/test_refparser.py

## Purpose
This file is a minimal parser smoke test for reference-policy interface syntax. It feeds a multi-interface reference-policy snippet through `sepolgen.refparser.parse()`.

## Important Tests And Exercised APIs
`TestParser.test_interface_parsing()` embeds three `interface(...)` definitions with summary/param comments, `gen_require`, `allow` rules, `typeattribute`, conditionals, optional policy, tunable policy, and interface calls. The test calls `refparser.parse(interface_example)`.

## Control Flow
The parser result is assigned to `h`, and the rest of the detailed assertions are commented out. The test therefore passes if parsing completes without exception.

## State And Persistence
All state is in memory. The parser may generate yacc table/debug artifacts depending on parser configuration and working directory, which the tests Makefile cleans.

## Dependencies And Integration Points
It imports `sepolgen.refparser` and `sepolgen.refpolicy`. It indirectly depends on yacc/lex parser generation and grammar action code.

## Risks And Edge Cases
Because all semantic assertions are commented, malformed parse trees could pass. The test still catches syntax-level parser regressions for a representative interface sample, but it is not a structural parser test.

## Test Signals
This is a parser smoke signal. `test_interfaces.py` supplies stronger semantic validation for parsed interface data.
