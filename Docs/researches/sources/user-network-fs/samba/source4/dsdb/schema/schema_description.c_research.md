# sources/user-network-fs/samba/source4/dsdb/schema/schema_description.c

## Purpose
`schema_description.c` formats DSDB schema attributes, classes, dITContentRules, and extended info into LDAP-style schema description strings.

## Important APIs, Types, and Functions
Attribute formatting is handled by `schema_attribute_description`, `schema_attribute_to_description`, and `schema_attribute_to_extendedInfo`. Class and rule formatting is handled by `schema_class_description`, `schema_class_to_description`, `schema_class_to_dITContentRule`, and `schema_class_to_extendedInfo`. The `APPEND_ATTRS` macro formats attribute lists with OpenLDAP line wrapping rules.

## Control Flow and Behavior
The generic description helpers build a parenthesized schema string by appending optional fields only when supplied: name, equality, substring, syntax, single-value, no-user-modification, ranges, property GUIDs, indexing, system-only, auxiliary classes, superclass, class category, must/may attributes, and schema GUID. The wrapper functions extract the relevant fields from `dsdb_attribute` or `dsdb_class`, use schema query helpers to compute inherited attributes where needed, and format AD schema subentry strings.

## State and Persistence Behavior
The file is pure formatting logic. It allocates returned strings on the caller's talloc context and does not mutate schema objects.

## Dependencies and Integration Points
It depends on `samdb.h`, NDR GUID helpers, schema query helpers, talloc append helpers, and DSDB schema constants. It feeds schema export, operational schema attributes, and human-readable schema introspection.

## Risks and Edge Cases
The formatter assumes names/OIDs are already valid and does not escape embedded quotes or special characters. `schema_attribute_to_description` assumes `attribute->syntax` is non-NULL. `schema_class_to_dITContentRule` does not guard a missing auxiliary class lookup before passing it to `dsdb_attribute_list`, so corrupt schema can crash. Formatting differences by target can affect backend parser acceptance.

## Test Signals
Tests should cover optional fields, multi-attribute wrapping, all objectClassCategory cases, AD schema subentry output, dITContentRule output with auxiliary classes, GUID/range/index/system-only extended info, unusual names requiring escaping, and missing syntax or auxiliary class error handling.
