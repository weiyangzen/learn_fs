# sources/storage-engines/tikv/components/tidb_query_aggr/src/impl_max_min.rs

Purpose: implements `MAX` and `MIN` aggregation with shared generic machinery. `Extremum` binds an aggregate expression type and comparison direction; `Max` replaces stored values when current order is `Less`, and `Min` when it is `Greater`.

Important APIs and control flow: `AggrFnDefinitionParserExtremum<E>` validates one child, reads child eval type, unsigned integer flag, and output collation, checks the root output type, appends one schema column/expression, and selects a concrete implementation. General ordered types use `AggFnExtremum<T,E>`, ints use `AggFnExtremumForInt<E, IS_UNSIGNED>`, bytes use `AggFnExtremumForBytes<C,E>` with collation-specific `Collator`, and enum/set have dedicated string-comparison implementations.

State and persistence behavior: each state stores an optional owned extremum value and updates only for non-null inputs. Bytes, enum, set, and generic owned values are cloned into state; integer state stores copied `i64`. There is no persistence outside the aggregate state object.

Dependencies and integration: depends on `tidb_query_datatype` collation support, `FieldTypeFlag::UNSIGNED`, `match_template_collator`, `VectorValueExt`, and aggregate traits/macros from `lib.rs`. Parser dispatch in `parser.rs` maps `ExprType::Max` and `ExprType::Min` to this implementation.

Risks and test signals: correctness is sensitive to unsigned integer ordering, collation selection, and MySQL-specific enum/set string semantics. Several implementations use unsafe lifetime transmutes to reborrow owned values for comparison; this is localized but high-risk if data-type ownership contracts change. Tests cover max/min updates, null handling, vector updates, collations, signed/unsigned integer behavior, parser integration, and illegal output types.
