# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_resptype.c

`iter_resptype.c` classifies DNS responses for the iterator. `response_type_from_cache()` handles cached messages and only distinguishes terminal answers from CNAME-continuation responses, assuming cached throwaway/lame/referral cases are not delivered through this path.

`response_type_from_server()` classifies wire responses as answer, referral, CNAME, throwaway, lame, or recursion-lame. It drops TC responses, treats most non-NOERROR/NXDOMAIN rcodes as throwaway, follows relevant CNAMEs, detects ANY/NS answer-section referrals, and uses authority-section SOA/NS relationships against the queried delegation point to distinguish NODATA, referrals, and lameness.

Recursive-lame detection is based on RA without AA when the iterator did not send RD. Empty NOERROR/NODATA messages are retried a limited number of times through `empty_nodata_found` before being accepted as answers.

The file is central to iterator state transitions after receiving a server response, especially deciding whether to cache, chase a CNAME, follow a referral, mark a server lame, or try another target.
