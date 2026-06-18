# File Research: sources/local-fs/udftools/include/osta_udf.h

Packed UDF-specific definitions based on OSTA UDF 2.60.

Defines:
- UDF compressed Unicode charspec constants.
- Standard entity identifier strings.
- Identifier suffix layouts for domain, UDF, implementation, and application IDs.
- Logical Volume Integrity implementation-use structure.
- Implementation Use Volume Descriptor implementation-use structure.
- UDF type 2 partition maps.
- Virtual, sparable, and metadata partition maps.
- VAT layouts for UDF 1.50 and UDF 2.00+.
- Sparing table and sparing entry layouts.
- Metadata file type constants.
- Allocation descriptor implementation-use flags.
- UDF-specific strategy and real-time file type constants.
- UDF-defined extended attributes.
- UDF-defined stream identifiers.
- OS class and OS identifier constants, including Linux/FreeBSD/NetBSD values.

Key role: supplements ECMA-167 with UDF profile-specific identifiers and structures required by mkudffs and UDF metadata tools.

No runtime behavior.
