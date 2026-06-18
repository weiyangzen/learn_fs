# sources/user-network-fs/samba/source4/kdc/tests/sdb_to_hdb_test.c

## Purpose

`sdb_to_hdb_test.c` tests the Heimdal conversion implementation in `source4/kdc/sdb_to_hdb.c`. It verifies encoding of SDB public-key trust and certificate mapping structures into Heimdal HDB extension values.

## Important APIs, Types, and Functions

The tested functions are `sdb_pub_key_to_hdb_key_trust_val()`, `sdb_cert_mapping_to_hdb_key_trust_val()`, and `sdb_certificate_mappings_to_hdb_ext()`. Output types include `HDB_Ext_KeyTrust_val`, `HDB_Ext_CertificateMapping`, and `HDB_Ext_CertificateMappings`.

## Control Flow

The test list starts with RSA public-key DER encoding: empty key, high-bit modulus/exponent needing DER leading zero bytes, and normal values. It then checks individual certificate mapping fields, all fields together, and mapping collections with zero, one, and two entries.

## State and Persistence Behavior

The file has no persistent state. Inputs are stack locals or constant blobs. Output allocations are freed with `free()` or Heimdal generated free helpers after assertions.

## Dependencies and Integration Points

It includes `../sdb_to_hdb.c` directly, `hdb_asn1.h`, cmocka, and data blob helpers. The KDC build script builds it as `test_sdb_to_hdb` under Heimdal. It validates data that PKINIT/key-trust paths consume through Heimdal HDB extensions.

## Risks and Edge Cases

DER integer sign handling is the main edge case: values with the top bit set must be encoded with a leading zero byte. Empty public-key values still encode as a valid RSA public-key sequence with zero integers. Multi-mapping tests verify collection metadata more than every encoded child field.

## Test Signals

Signals are exact DER byte comparisons, null-field checks for empty mappings, strong-mapping flag propagation, enforcement mode and valid-start propagation, and clean allocation/free behavior under memory checkers.
