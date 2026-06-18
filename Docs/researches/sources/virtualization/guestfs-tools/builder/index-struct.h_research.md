# File Research: sources/virtualization/guestfs-tools/builder/index-struct.h

## Scope

Header defining the C structures produced by the virt-builder index parser.

## Data Structures

- `struct section`: linked list node with section name and field list.
- `struct field`: linked list node with key, optional subkey, and value.
- `struct parse_context`: parser result, comment detection flag, input file, program name, and error suffix.

## APIs

- Declares context initialization/freeing.
- Declares recursive section and field free helpers.

## Risks And Invariants

- `seen_comments` is part of validator compatibility checks for old virt-builder versions.
- Ownership is heap-based C strings and linked nodes; callers must use the declared cleanup helpers.
