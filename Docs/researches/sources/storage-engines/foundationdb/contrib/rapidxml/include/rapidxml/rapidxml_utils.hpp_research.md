# sources/storage-engines/foundationdb/contrib/rapidxml/include/rapidxml/rapidxml_utils.hpp

## Purpose

`rapidxml_utils.hpp` provides small high-level utilities for simple RapidXML use cases: loading a full file or stream into a zero-terminated buffer and counting child nodes or attributes.

## Important APIs, Types, and Functions

- `file<Ch>`:
  - `file(const char* filename)` opens a binary input file, measures it with seek/tell, reads it into `std::vector<Ch>`, and appends a zero terminator.
  - `file(std::basic_istream<Ch>& stream)` reads an existing stream through `istreambuf_iterator`, checks stream failure, and appends a zero terminator.
  - `data()` returns mutable or const pointer to the vector buffer.
  - `size()` returns `m_data.size()`, including the terminating zero.
- `count_children(xml_node<Ch>* node)` iterates `first_node()` / `next_sibling()`.
- `count_attributes(xml_node<Ch>* node)` iterates `first_attribute()` / `next_attribute()`.

## Control Flow

The filename constructor opens with `ios::binary`, disables `skipws`, seeks to end to determine size, seeks back, resizes the vector to `size + 1`, reads exactly `size` characters, and stores `0` at the end. The stream constructor disables `skipws`, assigns all characters from the stream buffer to the vector, checks `fail()`/`bad()`, and pushes a terminator.

Counting helpers are straightforward linear linked-list scans over the DOM.

## State and Persistence Behavior

`file<Ch>` owns its buffer in `m_data`; the pointer returned by `data()` remains valid until the `file` object is destroyed or its vector is otherwise reallocated internally. This fits RapidXML's requirement that the mutable parse buffer outlive the document.

The reported `size()` includes the trailing terminator, which callers must remember if they need original byte/character count.

## Dependencies and Integration Points

The file includes `rapidxml.hpp`, `<vector>`, `<string>`, `<fstream>`, and `<stdexcept>`. It is intended for simple callers that do not already have their XML payload loaded into mutable memory.

## Risks and Edge Cases

- `tellg()` is cast to `size_t` without checking for failure or negative position; unusual streams or very large files can misbehave.
- The filename constructor does not verify that `read()` consumed the expected number of characters after resizing.
- `size()` including the null terminator can lead to off-by-one mistakes.
- Loading the entire file into memory is unsuitable for very large XML traces or untrusted input sizes.
- Constructors throw `std::runtime_error` on open/read failures, independent of RapidXML's `RAPIDXML_NO_EXCEPTIONS` parse-error mode.
- `data()` returns `&m_data.front()`; because constructors always append/allocate at least one terminator, it is valid for constructed objects, but this pattern would be unsafe if future code allowed empty vectors.

## Test Signals

Tests should load a real file, an empty file, a stream with embedded whitespace, a stream failure case, and verify that the buffer is mutable and zero-terminated. Count helpers should be tested with zero, one, and multiple children/attributes and after DOM mutations.
