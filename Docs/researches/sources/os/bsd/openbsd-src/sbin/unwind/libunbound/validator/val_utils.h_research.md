# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_utils.h

`val_utils.h` declares the shared helper API for unwind's embedded libunbound DNSSEC validator. It defines `enum val_classification`, which is the validator's response-shape taxonomy: positive answers, CNAME/DNAME chains, NODATA, NXDOMAIN, CNAME-with-no-final-answer, referrals, ANY answers, and unknown/untyped cases.

The header exposes the major validation utilities used by `validator.c`: response classification, signer discovery, RRset signature validation, DNSKEY validation through DS or trust anchors, DS usability checks, wildcard detection, CNAME chasing, chased-reply extraction, authority RRset removal, nonsecure RRset cleanup, and marking unchecked RRsets indeterminate or insecure.

It also declares chain-of-trust support helpers: `val_find_DS()` can synthesize a DS denial message from caches, `val_blacklist()` carries forward bad upstream/origin avoidance, `val_has_signed_nsecs()` verifies that negative proofs are present, and `val_favorite_ds_algo()` chooses a supported DS algorithm.

Important coupling: this header bridges the validator core to packed RRsets, reply/query structures, trust anchors, key entries, regional allocation, rrset cache, NSEC/NSEC3 proof helpers, and EDE bogus reason reporting.
