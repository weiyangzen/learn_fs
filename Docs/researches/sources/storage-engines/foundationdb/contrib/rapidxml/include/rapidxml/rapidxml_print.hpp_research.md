# sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml_print.hpp

## Purpose

`rapidxml_print.hpp` serializes RapidXML DOM nodes back to XML through output iterators or C++ streams. It implements escaping, indentation, node-type-specific formatting, and `operator<<` integration when streams are enabled.

## Important APIs, Types, and Functions

- `print_no_indenting` suppresses tab indentation and newline insertion.
- `internal::copy_chars()` copies raw character ranges.
- `internal::copy_and_expand_chars()` writes text while escaping `<`, `>`, `'`, `"`, and `&`, with a `noexpand` character that can be copied verbatim for quote selection.
- `internal::fill_chars()` emits repeated indentation characters.
- `internal::find_char<Ch, ch>()` scans a range for a character.
- `internal::print_node()` dispatches by `node_type`.
- Node-specific printers include:
  - `print_children()`
  - `print_attributes()`
  - `print_data_node()`
  - `print_cdata_node()`
  - `print_element_node()`
  - `print_declaration_node()`
  - `print_comment_node()`
  - `print_doctype_node()`
  - `print_pi_node()`
- Public APIs:
  - `template <class OutIt, class Ch> OutIt print(OutIt out, const xml_node<Ch>& node, int flags = 0)`
  - Stream overload `std::basic_ostream<Ch>& print(...)` unless `RAPIDXML_NO_STREAMS` is defined.
  - `operator<<` for stream output unless streams are disabled.

## Control Flow

Public `print()` starts at `internal::print_node(out, &node, flags, 0)`. `print_node()` switches on `node->type()` and delegates to the matching printer. After each node, it appends a newline unless `print_no_indenting` is set.

Element printing emits an opening tag, attributes, and either:

- a self-closing tag when the node has no value and no children,
- inline text when the node has no children but has a value,
- inline text when the only child is `node_data`,
- or a multiline child subtree followed by the closing tag.

Attributes are printed with a quote choice heuristic: if the value contains `"`, single quotes are used and double quotes are not expanded; otherwise double quotes are used and single quotes are not expanded. Other XML-sensitive characters are escaped.

CDATA, comments, doctype, declaration, and PI nodes are emitted using fixed XML delimiters and raw node name/value slices as appropriate. Document nodes print their children.

## State and Persistence Behavior

The printer does not mutate the DOM. It reads `name()`, `name_size()`, `value()`, `value_size()`, child lists, and attribute lists. It supports non-null-terminated names and values because all output uses pointer-plus-size ranges.

Output state is owned by the caller-provided iterator or stream. The code assumes writes through the output iterator cannot fail except through the iterator/stream implementation.

## Dependencies and Integration Points

The header includes `rapidxml.hpp`. When `RAPIDXML_NO_STREAMS` is not defined it also includes `<ostream>` and `<iterator>`. It is the companion serializer for DOMs produced by `rapidxml.hpp` and manually constructed DOMs from the memory pool.

## Risks and Edge Cases

- The printer does not validate XML before serialization. Invalid names, illegal comment content (`--`), illegal CDATA content (`]]>`), and invalid PI payloads can produce malformed XML.
- Namespace prefixes are not reconstructed from `xml_node::prefix()`. Element printing copies only `node->name()`, which in this local RapidXML stores the local name when a prefixed element was parsed. Without manual name reconstruction or preserved attributes, round-tripping prefixed XML may lose prefixes in output.
- `print_attributes()` uses the stored attribute name exactly; attribute prefix handling depends on how the parser stored the name.
- Pretty printing uses tabs and appends a newline after every node, including top-level documents, which may not be byte-for-byte stable for tests expecting exact input preservation.
- `node_data` values are escaped, while `node_cdata`, comments, doctype, and PI values are copied raw. Caller-provided raw values can break XML syntax.
- Very large DOMs are serialized recursively through node traversal and may stress call stack or output iterator performance.

## Test Signals

Tests should cover all `node_type` cases, escaped text and attributes, quote-choice behavior, pretty vs `print_no_indenting`, non-null-terminated ranges, empty elements, element value vs sole data child precedence, stream overload behavior, and namespace/prefix round-trip expectations for this local RapidXML variant.
