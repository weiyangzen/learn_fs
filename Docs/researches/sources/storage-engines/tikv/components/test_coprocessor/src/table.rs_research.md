# sources/storage-engines/tikv/components/test_coprocessor/src/table.rs

## Purpose
This file defines table-schema fixtures for coprocessor tests. It maps named columns to IDs, builds TiDB protobuf table/index metadata, and creates table/index key ranges compatible with TiDB table encoding.

## Important APIs, Types, And Functions
`Table` stores table ID, handle column ID, ordered columns, name/ID lookup maps, and index definitions. `column_by_id`, `column_by_name`, and `Index` access columns case-insensitively. `table_info`, `columns_info`, and `index_info` build `tipb` metadata. Range helpers include `get_record_range_all`, `get_record_range`, `get_record_range_one`, `get_index_range_all`, and `get_table_prefix`.

`TableBuilder` collects columns, tracks a primary handle column, then `build` assigns a table ID, lookup maps, and index-column groups. For secondary indexes it appends the table handle to the index column list to model non-unique index entries.

## Control Flow And State
Table and column IDs are generated with the crate-global `next_id`. `add_col` updates handle selection when it sees `Column.index == 0`; if no explicit handle exists, `build` creates a synthetic handle ID. Index maps are derived from column metadata after all columns are registered.

## Persistence And Integration Points
The table object itself is in-memory metadata. It integrates with TiDB table key encoding, `tipb::{TableInfo, IndexInfo, ColumnInfo}`, and `KeyRange` protobufs consumed by `DagSelect` and coprocessor requests.

## Risks And Test Signals
`index_info` indexes directly into `self.idxs[&index]`, so invalid index IDs panic. `get_index_range_all` only encodes min/max i64 prefixes, which matches these simple fixtures but not arbitrary composite key domains. Case normalization can hide duplicate column names with different casing. Downstream test signals come from table scan/index scan correctness.
