# sources/user-network-fs/samba/source4/dsdb/tests/python/ldap_syntaxes.py

## Purpose

`ldap_syntaxes.py` tests Samba LDAP handling of two complex AD syntaxes: DN+String and DN+Binary. It dynamically adds schema attributes/classes using those syntaxes, creates objects with valid and invalid values, and verifies search matching requires the complete composite value rather than only the DN or only the string/binary component.

## Important APIs, Types, and Functions

The file uses `samba.tests.connect_samdb`, `system_session`, LDB scopes and errors, `uuid`, `time`, and random OID suffixes. `SyntaxTests.setUp()` connects to SamDB, stores the domain and schema DNs, then calls both schema setup helpers before every test.

Important helpers:

- `_setup_dn_string_test()` creates an `attributeSchema` with `attributeSyntax: 2.5.5.14`, `omSyntax: 127`, and DN+String `omObjectClass`, then creates a structural class that may contain that attribute.
- `_setup_dn_binary_test()` creates the analogous DN+Binary attribute with `attributeSyntax: 2.5.5.7` and DN+Binary `omObjectClass`, plus a containing class.
- `_get_object_ldif()` builds an object LDIF under `CN=Users` using the generated class and attribute value.

Test methods:

- `test_dn_string()` adds a valid `S:<len>:<string>:<dn>` value, verifies component-only searches do not match, verifies full DN+String search matches, and checks malformed length plus GUID/SID/random-DN substitutes fail with expected errors.
- `test_dn_binary()` does the same for `B:<len>:<hex-or-bytes>:<dn>`, including invalid binary length and non-DN target forms.

## Control Flow

Startup parses host/options/credentials and runs `TestProgram`. Each test instance creates fresh schema attribute/class definitions in `setUp()`. The syntax tests then build LDIF strings, call `add_ldif()` for valid setup/object creation, run subtree searches against the domain, and catch `LdbError` for invalid additions. Duplicate object DN attempts are expected to return `ERR_ENTRY_ALREADY_EXISTS` regardless of changed composite attribute contents.

## State and Persistence Behavior

The suite mutates the schema on every test setup by adding new attributes and classes named with the current epoch second and random OID components. It also creates test objects under `CN=Users`; the file does not register explicit cleanup for those objects or schema entries. As with other schema tests, schema additions are persistent and should be run against disposable test domains.

The generated attributes/classes are stored as instance variables (`dn_string_class_ldap_display_name`, `dn_string_attribute`, `dn_binary_class_ldap_display_name`, `dn_binary_attribute`, and class names) and used by the test methods.

## Dependencies and Integration Points

This test exercises DSDB schema extension, syntax parser/normalizer support for DN+String and DN+Binary, LDAP filter matching rules for composite values, DN validation inside composite syntaxes, and error mapping for invalid syntax versus constraint violations. It depends on the AD schema accepting the specified `omObjectClass` byte strings and on immediate availability of the new schema definitions after add.

## Risks and Edge Cases

The use of `time.strftime("%s")` can collide when setup runs more than once in the same second; random OID suffixes reduce OID collisions but not necessarily CN/class-name collisions. The tests do not force `schemaUpdateNow`, so they rely on Samba making new schema available quickly enough for immediate object creation. The `except LdbError` blocks assert codes only when an exception occurs; if an invalid add unexpectedly succeeds, several blocks do not call `fail()`, so a regression could be missed. Persistent schema/object additions can contaminate long-lived environments.

## Test Signals

Passing tests signal that Samba can add DN+String and DN+Binary schema attributes, instantiate objects containing those attributes, match only full composite values in LDAP filters, reject malformed length/value encodings with `ERR_INVALID_ATTRIBUTE_SYNTAX`, reject GUID/SID/random-string substitutes for required DNs with `ERR_CONSTRAINT_VIOLATION`, and preserve duplicate-DN behavior independently of attribute differences.
