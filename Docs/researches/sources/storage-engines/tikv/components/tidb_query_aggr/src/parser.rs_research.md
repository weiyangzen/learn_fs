# sources/storage-engines/tikv/components/tidb_query_aggr/src/parser.rs

Purpose: central parser dispatch for aggregate protobuf definitions. It turns a `tipb::Expr` aggregate node into a typed aggregate function plus the RPN child expression and output schema entries required by executors.

Important APIs and control flow: `AggrDefinitionParser` provides `check_supported`, default `parse`, and overridable `parse_rpn`. The default `parse` takes the first child, builds an `RpnExpression` with `RpnExpressionBuilder::build_from_expr_tree`, then passes root and expression to the concrete parser. `map_pb_sig_to_aggr_func_parser` maps supported `ExprType` values to parser structs for count, sum, avg, first, bit ops, max/min, and variance variants. `AllAggrDefinitionParser` is the public catch-all.

State and persistence behavior: no persistent state. It mutates the consumed protobuf expression by taking children and lets concrete parsers append to caller-owned `out_schema` and `out_exp` vectors.

Dependencies and integration: integrates aggregate implementation modules with `tidb_query_expr` RPN building and `tipb` expression metadata. It is the gateway used by executors before creating aggregate states.

Risks and test signals: default `parse` unwraps the first child, relying on prior `check_supported` to enforce arity. `AllAggrDefinitionParser::parse` unwraps parser dispatch, so unsupported aggregate types must be filtered before parsing. Concrete module tests exercise parser integration and blacklisted/mismatched expressions.
