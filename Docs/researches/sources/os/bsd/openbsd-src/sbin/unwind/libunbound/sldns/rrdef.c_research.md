# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/rrdef.c

`rrdef.c` implements DNS RR schema metadata. It defines the class lookup table and a large descriptor table mapping RR type codes to presentation names, minimum/maximum RDATA field counts, field RDF types, variable trailing RDF type, compression eligibility, and number of DNAME fields.

The descriptor table covers classic RFC1035 types, DNSSEC types, NSEC3, TLSA/SMIMEA, CDS/CDNSKEY, OPENPGPKEY, CSYNC, ZONEMD, SVCB/HTTPS, ILNP/EUI/URI/CAA, TKEY/TSIG, transfer/query pseudo-types, RESINFO, and DLV/TA. Unassigned gaps are represented as `TYPE###` descriptors with unknown/raw-style RDATA.

`LDNS_RDATA_FIELD_DESCRIPTORS_COMMON` allows direct array lookup for the contiguous low-numbered range; higher or split-out values are found by scanning. Unknown types fall back to descriptor zero.

The exported helpers return descriptors, minimum and maximum field counts, RDF type for a field index, RR type by textual name including `TYPE###`, and class by textual name including `CLASS###`. This file is the schema source used by `str2wire.c` to decide how to parse RDATA fields and where DNS name compression is allowed.
