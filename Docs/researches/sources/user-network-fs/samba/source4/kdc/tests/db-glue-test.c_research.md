# sources/user-network-fs/samba/source4/kdc/tests/db-glue-test.c

## Purpose

`db-glue-test.c` is a cmocka unit test translation unit for `source4/kdc/db-glue.c`. It includes the implementation directly and validates how LDAP/SAM database messages become SDB entries, key-trust public keys, certificate mappings, reversed DNs, and reversed Kerberos byte blobs.

## Important APIs, Types, and Functions

The file overrides `dsdb_functional_level()`, `lpcfg_strong_certificate_binding_enforcement()`, and `lpcfg_certificate_backdating_compensation()`. It tests `samba_kdc_message2entry()`, `get_key_trust_public_keys()`, `parse_certificate_mapping()`, `get_certificate_mappings()`, `reverse_dn()`, and `reverse_krb5_data()` using synthetic `ldb_message` objects.

## Control Flow

`main()` registers many subunit cmocka tests. Message conversion tests cover empty, minimal, empty binary-DN, and populated `msDS-KeyCredentialLink` cases. Key trust tests parse BCRYPT RSA, TPM 2.0, and DER SubjectPublicKeyInfo data and reject malformed duplicate or invalid entries. Certificate mapping tests parse X509 tags and invalid forms, then integration tests combine `altSecurityIdentities`, `whenCreated`, binding enforcement, and backdating compensation. Utility tests cover DN delimiter variants and in-place data reversal.

## State and Persistence Behavior

Each test creates its own talloc context and frees SDB output. The only shared mutable state is the pair of global configuration override integers. No real SAM database is changed; LDB contexts are local scaffolding.

## Dependencies and Integration Points

It includes `../db-glue.c`, cmocka, LDB, SAMDB, SDB, talloc, data blob, and debug headers. The KDC build script compiles it as `test_db_glue` under Heimdal builds. It protects PKINIT/key-trust inputs consumed by later HDB conversion.

## Risks and Edge Cases

Including the implementation gives access to static helpers but can miss link-boundary issues. The tests document subtle behavior: duplicate certificate tags keep the last value, issuer DNs are reversed, serial hex is byte-reversed, malformed hex is rejected, and SKI/public-key mappings are strong while RFC822 alone is not.

## Test Signals

Strong signals are successful `test_db_glue` subunit output, byte-for-byte modulus/exponent checks for BCRYPT/TPM/DER key material, expected mapping enforcement/backdating values, malformed input rejection, and broad DN reversal coverage.
