# sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml.hpp

## Purpose

`rapidxml.hpp` is the header-only core of RapidXML 1.13 as vendored into FoundationDB, with local extensions for XML namespace tracking/validation and stream-oriented partial parsing. It defines the parser flags, error model, DOM types, memory pool allocator, in-place XML parser, namespace lookup helpers, and static lookup tables used by sibling headers.

The parser is optimized for mutable, zero-terminated XML buffers. By default it writes terminators into the input, expands entity references in place, and stores node and attribute names/values as pointers into the original buffer. This is a high-performance design, but it makes input lifetime, mutability, and parse flags part of the API contract.

## Important APIs, Types, and Functions

- Error configuration:
  - `RAPIDXML_PARSE_ERROR(what, where)` and `RAPIDXML_EOF_ERROR(what, where)` either throw exceptions or call `parse_error_handler()` when `RAPIDXML_NO_EXCEPTIONS` is defined.
  - `parse_error` carries a typed `where<Ch>()` pointer into the source buffer.
  - `validation_error` reports namespace validation failures.
  - `eof_error` is declared as a `parse_error` subtype, but its constructor is private in this file, so direct construction is not externally useful.
- Parser flags:
  - Stock flags include `parse_no_data_nodes`, `parse_no_element_values`, `parse_no_string_terminators`, `parse_no_entity_translation`, `parse_no_utf8`, `parse_declaration_node`, `parse_comment_nodes`, `parse_doctype_node`, `parse_pi_nodes`, `parse_validate_closing_tags`, `parse_trim_whitespace`, and `parse_normalize_whitespace`.
  - Compound flags are `parse_default`, `parse_non_destructive`, `parse_fastest`, and `parse_full`.
  - Local extensions include `parse_open_only`, `parse_parse_one`, and `parse_validate_xmlns` declarations. The first two affect parser control flow; `parse_validate_xmlns` is declared but is not automatically invoked by `parse()` in this file.
- `memory_pool<Ch>`:
  - Allocates `xml_node`, `xml_attribute`, and strings using a static pool first, then dynamically allocated blocks.
  - Exposes `allocate_node()`, `allocate_attribute()`, `allocate_string()`, `clone_node()`, `clear()`, and `set_allocator()`.
  - Adds cached strings for `nullstr()`, `xmlns_xml()`, and `xmlns_xmlns()` for namespace lookup helpers.
- `xml_base<Ch>`:
  - Common name/value/size/parent storage for nodes and attributes.
  - Setters store non-owning pointers; callers are responsible for lifetime unless strings come from the pool.
- `xml_attribute<Ch>`:
  - Represents a linked-list attribute with `previous_attribute()`, `next_attribute()`, `document()`, `xmlns()`, `xmlns_size()`, `local_name()`, and `local_name_size()`.
  - Namespace methods lazily compute/cache the namespace URI and local-name pointer.
- `xml_node<Ch>`:
  - Stores node type, prefix, cached namespace URI, child list, and attribute list.
  - Provides child and attribute lookup (`first_node`, `last_node`, `previous_sibling`, `next_sibling`, `first_attribute`, `last_attribute`) plus mutation (`prepend_node`, `append_node`, `insert_node`, removals, and attribute equivalents).
  - Adds namespace-aware `first_node()` and `last_node()` overload shape: when a name is supplied without an explicit namespace, it assumes the same namespace as the current node.
  - `xmlns_lookup()` walks ancestor attributes looking for `xmlns` or `xmlns:prefix`, with hard-coded handling for `xml` and `xmlns`.
  - `validate()` recursively checks that element and attribute namespace bindings exist and that duplicate attributes are not present either by raw name or by local-name-plus-namespace.
- `xml_document<Ch>`:
  - Inherits from both `xml_node<Ch>` and `memory_pool<Ch>`.
  - `parse<Flags>(Ch *text, xml_document<Ch> *parent = 0)` clears current tree links, parses BOM and top-level nodes, and returns the input pointer at the parse stop point.
  - `parse<Flags>(Ch *text, xml_document<Ch>& parent)` forwards to the pointer overload.
  - `clear()` removes nodes/attributes and clears the pool.
  - `fixup<Flags>(xml_node<Ch>* element, bool recurse)` terminates and decodes a previously parsed subtree, particularly useful with partial/open parsing.
  - `validate()` runs namespace validation over top-level children.

## Control Flow

Parsing starts in `xml_document::parse<Flags>()`. It clears the current node and attribute links, optionally attaches the document under a parent document's first node, skips a UTF-8 BOM, then repeatedly skips whitespace and expects `<`. Each markup item is dispatched through `parse_node<Flags>()`.

`parse_node()` dispatches by the first character after `<`:

- default: `parse_element()`
- `?`: XML declaration or PI
- `!`: comment, CDATA, DOCTYPE, or unknown declaration-like markup skipped to `>`

`parse_element()` creates a `node_element`, splits an optional `prefix:local` element name, parses attributes, then either parses nested contents for open tags, handles self-closing tags, or reports syntax errors. Name/prefix terminators are written unless `parse_no_string_terminators` is set.

`parse_node_contents()` loops over child markup and text until a closing tag, EOF, or parse flag stops it. Data is routed through `parse_and_append_data()`, which performs entity expansion, optional whitespace normalization/trimming, optional `node_data` creation, optional parent element value assignment, and optional terminator insertion. The function returns the character that stopped text scanning because terminator insertion may have overwritten it.

Attribute parsing in `parse_node_attributes()` reads attribute names, appends each attribute immediately, enforces `=`, handles quote choice, expands entity references in value text, stores value spans, and writes terminators unless disabled. Attribute whitespace normalization is explicitly masked out even when element text normalization is enabled.

Namespace validation is not part of the parse loop. Callers must invoke `validate()` explicitly after parsing if they want namespace binding and duplicate-attribute checks.

## State and Persistence Behavior

The DOM is memory-backed by `memory_pool`. Nodes, attributes, cached namespace strings, and allocated strings are invalidated by `memory_pool::clear()` or document destruction. Parsed names/values generally point into the original input buffer, so the input buffer must outlive the DOM unless callers clone/copy strings into the pool.

The parser mutates source text by default. Mutations include null terminators after names/values and in-place replacement of entity references/numeric character references. `parse_non_destructive` prevents terminators and entity translation but also requires users to respect `*_size()` because strings are not guaranteed to be null-terminated.

Several object fields are intentionally undefined unless related pointers are non-null, for performance. For example, `m_last_node` is meaningful only when `m_first_node` is set, and sibling pointers are meaningful only when a parent is set. Misusing raw internals or calling traversal functions outside their preconditions can assert or produce undefined behavior.

Namespace URI and local-name fields are cached lazily inside mutable members. If attributes or prefixes are modified after first lookup, cached namespace values may become stale because mutation methods do not invalidate `m_xmlns` or `m_local_name`.

## Dependencies and Integration Points

The header depends on the C++ standard library unless `RAPIDXML_NO_STDLIB` is defined. Default builds use `<cstdlib>`, `<cassert>`, `<new>`, and `<stdexcept>`. It is consumed directly by `rapidxml_iterators.hpp`, `rapidxml_print.hpp`, and `rapidxml_utils.hpp`.

Build-time customization is through macros such as `RAPIDXML_NO_EXCEPTIONS`, `RAPIDXML_NO_STDLIB`, `RAPIDXML_STATIC_POOL_SIZE`, `RAPIDXML_DYNAMIC_POOL_SIZE`, and `RAPIDXML_ALIGNMENT`. Users disabling exceptions must provide `rapidxml::parse_error_handler()`.

The likely repository integration is XML parsing for FoundationDB utilities or tests where a lightweight header-only parser is preferred. The namespace extensions suggest local callers need XPath-like namespace-aware lookup or validation.

## Risks and Edge Cases

- Input mutation is easy to overlook. Passing string literals, read-only memory, mmap pages without write permission, or buffers that do not outlive the document will break the parser contract.
- `xml_node::remove_all_nodes()` and `remove_all_attributes()` clear parent pointers but leave some last/sibling fields stale; this is consistent with internal preconditions but unsafe for external stale pointers.
- `clone_node()` shares name and value pointers rather than copying string data, so clones can dangle when the source buffer is released.
- Namespace lookup allocates temporary attribute names with `new[]` on every uncached lookup and does not use the memory pool for that temporary.
- Namespace caches can become stale after DOM mutation.
- `parse_validate_xmlns` is declared but not wired into `parse()`, so setting the flag alone does not appear to validate namespaces.
- `parse_open_only`/`parse_parse_one` partially parse streams and return the stop pointer, but callers must carefully use `fixup()` or subsequent parsing to finish names/values and tree state.
- `parse_and_append_data()` trims by looking at `end - 1`; all-whitespace or empty data with trimming enabled should be tested because this code assumes there is a preceding character to inspect.
- Closing tag validation compares only `node->name()` and not the parsed prefix. For prefixed elements this may validate local name only, depending on how closing names are parsed.

## Test Signals

Useful tests should include destructive vs non-destructive parsing, entity translation and numeric character references, UTF-8 vs `parse_no_utf8`, whitespace trimming/normalization, comments/PI/doctype inclusion flags, CDATA with and without data nodes, closing tag validation, partial parsing with `parse_open_only` and `parse_parse_one`, and explicit namespace validation.

Namespace tests should cover default namespaces, prefixed element/attribute lookup, built-in `xml` and `xmlns` prefixes, unbound prefixes, duplicate raw attributes, duplicate local-name-plus-namespace attributes, and cache behavior after mutation.
