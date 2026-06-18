# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_resptype.h

`iter_resptype.h` defines `enum response_type` for iterator response interpretation: untyped, answer, referral, CNAME, throwaway, lame, and recursion-lame.

It declares the two classifiers: `response_type_from_cache()` for cached messages and `response_type_from_server()` for wire responses. The server classifier takes the sent-RD state, request, active delegation point, and empty-NODATA retry counter.

This header is the contract between response parsing/scrubbing and the iterator control flow that decides the next resolution step.
