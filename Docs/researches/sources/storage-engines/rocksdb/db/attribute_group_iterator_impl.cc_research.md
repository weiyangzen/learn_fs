# sources/storage-engines/rocksdb/db/attribute_group_iterator_impl.cc

## Purpose
Implements minimal storage population for attribute-group iteration across multiple column families.

## Important APIs and Control Flow
Defines empty constants `kNoAttributeGroups` and `kNoIteratorAttributeGroups`. `AttributeGroupIteratorImpl::AddToAttributeGroups` iterates over `autovector<MultiCfIteratorInfo>` items and appends `(ColumnFamilyHandle*, WideColumns*)` pairs to `attribute_groups_`, referencing each child iterator's `columns()`.

## State, Dependencies, and Risks
The method stores pointers into child iterator column data, so validity is tied to the current iterator position and the wrapped `MultiCfIteratorImpl` lifecycle. It depends on `MultiCfIteratorInfo`, `Iterator::columns()`, and `rocksdb/attribute_groups.h` types. Risks include stale references if callers retain `attribute_groups()` after movement/reset, although the wrapper clears and repopulates on position changes. Tests are likely in multi-CF/attribute-group iterator suites.
