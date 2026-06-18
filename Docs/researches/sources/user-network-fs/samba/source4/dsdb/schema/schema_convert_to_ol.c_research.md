# sources/user-network-fs/samba/source4/dsdb/schema/schema_convert_to_ol.c

## Purpose
`schema_convert_to_ol.c` linearizes Samba's AD schema into OpenLDAP or Fedora DS schema text, applying caller-supplied mapping rules for skipped names, renamed attributes/classes, and remapped OIDs.

## Important APIs, Types, and Functions
The public entry point is `dsdb_convert_schema_to_openldap`. Internal mapping structures are `struct attr_map` and `struct oid_map`. `print_schema_recursive` emits object classes recursively from `top` down using `schema_class_description` and full attribute-list helpers.

## Control Flow and Behavior
`dsdb_convert_schema_to_openldap` parses the mapping text line by line, ignoring blanks and comments. Lines beginning with a digit map OIDs; nonnumeric `old:new` lines map attribute or objectClass names; bare names are skipped. It fetches the loaded schema from the LDB context, emits all non-skipped attributes with syntax/equality/substring data from the schema syntax table, then recursively emits class descriptions starting at `top`.

## State and Persistence Behavior
No schema state is changed. Output text is allocated under a temporary context, then stolen onto the LDB context before return. Mapping tables are transient.

## Dependencies and Integration Points
The file depends on loaded schema access, schema query helpers, schema description formatting, string-list utilities, locale/ctype functions, and talloc string append helpers. It is used by tooling or provisioning paths that need schema export for non-Samba LDAP backends.

## Risks and Edge Cases
The mapping parser ignores the last line if the mapping string is not newline-terminated because it stops when `strchr(line, '\n')` fails. Remapped OID/name pointers may point into the mutable mapping buffer, so output construction must complete before the temporary context is freed. Recursion assumes a sane class hierarchy below `top`. Skip/remap matching is case-insensitive, but generated schema validity depends on avoiding backend builtin conflicts and unsupported syntax OIDs.

## Test Signals
Tests should cover OpenLDAP and Fedora DS output modes, invalid target handling, skip lines, OID remaps, name remaps, class hierarchy recursion, missing `top`, syntax remapping, non-newline-terminated mapping text, and generated schema accepted by target parsers.
