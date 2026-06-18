# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnserver.c

DNS request-answering logic shared by UDP and TCP servers. `dnserver()` takes a parsed request message, creates one reply for one question, validates request code/type/class, enforces recursion policy, resolves answers, attaches authority/additional data, and sets DNS flags/response codes.

For local authoritative areas, AXFR/IXFR are rejected here except TCP AXFR is handled separately in `dnstcp.c`. Non-authoritative requests with recursion disabled return empty success. Recursive and nonrecursive lookup both pass through `doextquery()`, which calls `dnresolve()` and strips negative cached RRs from public answers.

Authority handling adds NS records when known, SOA records for local negative answers, and cached negative SOA owners when available. `hint()` adds A/AAAA glue for NS/MX/mail records from cache or DB.

Risks include pointer assumptions around `reqp->qd`, RR list mutation/ownership, and response-code propagation only when expected DN/cache state exists.
