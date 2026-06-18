# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ipsec.h

Public IPsec DOI header.

It defines `struct ipsec_exch`, the DOI-specific exchange state containing negotiated hash/auth/group/PRF state, DH values, SKEYID material, phase-2 IDs, keymat length, and ISAKMP configuration attributes. It also defines `struct ipsec_sa` for phase-1 key state plus phase-2 selectors and ports, and `struct ipsec_proto` for encapsulation, authentication, key length/rounds, replay window, and directional key material.

The exported API covers DOI registration, transform/attribute decoding, HASH payload handling, DH generation/saving, configured ID construction/parsing/rendering, key length calculation, initial-contact notification, ID cloning, and SA lookup by destination/SPI/protocol.
