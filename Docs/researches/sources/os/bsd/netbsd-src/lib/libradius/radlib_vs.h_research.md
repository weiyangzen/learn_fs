# File Research: sources/os/bsd/netbsd-src/lib/libradius/radlib_vs.h

This public vendor-specific RADIUS header defines Microsoft vendor id `311` and RFC 2548 Microsoft attribute codes, including MS-CHAP response/error/password/challenge attributes, MPPE encryption policy/types/send/recv keys, RAS metadata, ARAP password fields, filters, accounting auth/EAP type, DNS/NBNS server attributes, and ARAP challenge.

It defines `SALT_LEN` as 2 for MPPE key decoding and forward-declares `struct rad_handle`. The API adds vendor-specific helpers to parse a vendor attribute, put vendor address/raw/int/string attributes, and demangle Microsoft MPPE keys. These functions complement the base `radlib.h` API without exposing private handle layout.
