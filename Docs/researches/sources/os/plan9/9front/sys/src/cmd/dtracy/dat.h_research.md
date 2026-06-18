# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/dat.h

This header defines the main internal data model for dtracy: types, symbols, AST nodes, statements, clauses, enabled probe entries, and aggregation metadata.

Key structures:
- `Type`: integer, pointer, and string type descriptors with size/sign/reference fields.
- `Symbol`: global symbols, currently mostly variables (`SYMVAR`) with kernel variable index and type.
- `Node`: expression AST with node kind, operator, child pointers, symbol/string/number payload, source line, type, and analysis fields used by cast elision and record insertion.
- `Stat`: clause statements for expressions, print/printf, and aggregations.
- `Clause`: parsed probe clause with probes, predicate bytecode, and statements.
- `Enab`: runtime epid-to-clause mapping from kernel enablement data.
- `Agg`: user-space wrapper around `DTAgg` plus display name.

Important implementation notes:
- `SYMHASH` is 256 for global symbol buckets.
- Custom Plan 9 format pragmas are declared for node/type/operator diagnostics.
- Globals such as `dflag`, `noagg`, `aggid`, and `aggs` are shared across compilation, execution, and aggregation handling.
