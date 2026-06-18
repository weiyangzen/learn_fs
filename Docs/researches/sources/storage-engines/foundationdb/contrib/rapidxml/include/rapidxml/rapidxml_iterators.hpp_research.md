# sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml_iterators.hpp

## Purpose

`rapidxml_iterators.hpp` adds lightweight STL-style bidirectional iterators over RapidXML child nodes and attributes. It is a small convenience layer on top of `rapidxml.hpp` linked-list traversal methods.

## Important APIs, Types, and Functions

- `node_iterator<Ch>`:
  - `node_iterator()` constructs an end/null iterator.
  - `node_iterator(xml_node<Ch>* node)` starts at `node->first_node()`.
  - `operator*()` and `operator->()` expose the current `xml_node`.
  - Prefix and postfix increment move to `next_sibling()`.
  - Prefix and postfix decrement move to `previous_sibling()`.
  - Equality compares the underlying node pointer.
- `attribute_iterator<Ch>`:
  - Mirrors `node_iterator`, but starts at `node->first_attribute()` and moves through `next_attribute()` / `previous_attribute()`.

The typedefs advertise `std::bidirectional_iterator_tag`, `std::ptrdiff_t`, pointer/reference, and value type members expected by older STL algorithms. The file relies on `rapidxml.hpp` for `<cassert>` and standard-library typedef availability in normal configurations.

## Control Flow

Both iterators store only one pointer. Construction from a parent node immediately moves to the first child or first attribute. Increment/decrement methods assert that the current pointer is non-null, then ask RapidXML's linked-list APIs for the adjacent item. Comparison is pointer identity.

## State and Persistence Behavior

Iterator validity is tied to the underlying DOM node/attribute lifetime and list stability. Any DOM mutation that removes the current item or clears the document invalidates the iterator. Appending other siblings may leave existing iterators usable as long as the pointed item remains linked, but there is no formal invalidation tracking.

End is represented by a null current pointer. There is no stored parent pointer, so decrementing an end iterator cannot move to the last item. This differs from many container bidirectional iterators and should be treated as a limited traversal helper rather than a full container iterator.

## Dependencies and Integration Points

The only direct include is `rapidxml.hpp`. Callers that want range-like loops over child nodes or attributes can construct a begin iterator from a node and compare against the default iterator as the end sentinel.

## Risks and Edge Cases

- Postfix `operator++(int)` and `operator--(int)` call `++this` instead of `++(*this)` / `--(*this)`. In standard C++, incrementing `this` is invalid because `this` is not an lvalue iterator object. This is a serious compile-time defect if postfix operators are instantiated.
- Postfix decrement also increments rather than decrements, so even after the `this` bug is fixed it must call the decrement operator.
- Decrement asserts that a previous item exists; it cannot be used from end or from the first item.
- Constructors do not accept `const xml_node<Ch>*`, so these iterators do not support const DOM traversal.
- Equality operators are non-const member functions, which can reduce compatibility with STL algorithms expecting comparisons on const iterator objects.

## Test Signals

Compile tests should instantiate prefix and postfix increment/decrement for both iterator types. Runtime traversal tests should cover empty nodes, one child/attribute, multiple siblings, default end comparison, and behavior after removing the current item. Tests should also verify expected compiler diagnostics or fixes around the postfix operator bug.
