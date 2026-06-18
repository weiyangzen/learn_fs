<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/expression.h -->
# sources/security-integrity/audit-userspace/auparse/expression.h

## Purpose
Declares auparse search-expression internals: boolean expression nodes, comparison operators, virtual timestamp/type fields, regular-expression support, constructors, destruction, parsing, and evaluation against an `rnode` in the current `auparse_state_t`.

## Important APIs, types, and functions
`struct expr` is a tagged union keyed by `EO_*` operators. `field_id` covers virtual fields `EF_TIMESTAMP`, `EF_RECORD_TYPE`, and `EF_TIMESTAMP_EX`. Public hidden-library entry points are `expr_parse`, `expr_create_comparison`, timestamp constructors, `expr_create_field_exists`, `expr_create_regexp_expression`, `expr_create_binary`, `expr_eval`, and `expr_free`.

## Control flow
Callers either parse a user expression string or build expression trees directly, then `expr_eval` applies the tree to the parser event/record. Boolean nodes recurse through `v.sub`; comparison nodes hold field/value metadata; regexp nodes own compiled `regex_t`.

## State and persistence behavior
Expressions are heap-owned transient filters. They store copied field names, string values, numeric/timestamp precomputations, and compiled regex objects, but do not persist to disk.

## Dependencies and integration points
Depends on POSIX regex, `internal.h`, `auparse_state_t`, and `rnode`. It plugs into auparse searching through `opaque.expr` and record traversal.

## Risks and test signals
Risks are ownership leaks in unions, timestamp/numeric comparison mismatches, invalid regex cleanup, and false negatives because evaluation treats invalid terms as false. Test signals should cover parsed and constructed expressions, virtual fields, regex matches, missing fields, and negated invalid terms.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/expression.h -->
