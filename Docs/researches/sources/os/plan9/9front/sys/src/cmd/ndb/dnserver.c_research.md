# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnserver.c

Builds DNS replies for incoming DNS server requests.

Key elements:
- Public entry point `dnserver` consumes one question from a request message and fills a reply message.
- Validates opcode, RR type support, and class.
- Distinguishes authoritative local-area answers from recursive or non-recursive external answers.
- Enforces `cfg.nonrecursive` and `cfg.localrecursive` policies.
- Uses `doextquery` to call `dnresolve`, move positive answers into `mp->an`, and retain negative-cache RR information separately.
- Adds authority NS records for known parent zones and hint A/AAAA records for NS/MX/SRV/CNAME targets.
- Adds SOA records to negative responses when local authoritative area or cached negative SOA owner is known.
- Deduplicates answer, authority, and additional sections with `unique`.

Notable behavior:
- AXFR/IXFR are rejected here for locally owned areas; TCP AXFR has special handling in `dntcpserver.c`.
- Authority flag is set for local areas and transitive authoritative cached answers.
- If recursion was requested and no answer is found, response code can be copied from the queried owner `DN`.

Risks and quirks:
- The function mutates request and reply ownership of RR lists; callers must free the correct message lists afterward.
- Negative cached RRs are intentionally not returned as answer records.
