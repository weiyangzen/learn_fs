# File Research: sources/os/linux/linux-stable/fs/udf/osta_udf.h

## Summary
Defines Linux UDF-facing OSTA UDF 2.60 constants, entity identifiers, suffix structures, partition map structures, VAT structures, sparing tables, metadata partition records, extended attributes, stream identifiers, and OS identifiers.

## Main Responsibilities
- Declares standard UDF entity identifier strings such as virtual, sparable, metadata, VAT, sparing table, and logical volume info identifiers.
- Defines packed structures for domain, implementation, application, logical-volume-integrity, partition-map, VAT, sparing, metadata, and extended-attribute records.
- Provides UDF file type constants for VAT, metadata files, real-time files, and metadata bitmap files.
- Defines UDF OS class and OS ID values used by Linux LVID updates.

## Important Behavior
This header is on-disk ABI material. The packed layout and endian-typed fields are consumed by mount, partition, VAT, metadata, LVID, and EA code.

## Risks
Any structure layout or identifier change would break parsing of UDF media. The header mixes UDF 1.50, 2.00, 2.50, and 2.60 constructs, so consumers must check revision and map type before using fields.
