# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/query.c

Generic NDB query tool. It searches an NDB database for `attr value` and either prints full matching entries, a returned attribute, or all returned-attribute values depending on flags.

`-f` selects the NDB file, `-a` requests all matches instead of first matching returned attribute, and `-m` prints multiple values from the first returned entry. An optional fourth positional argument repeats the search multiple times, apparently for testing/timing.

The main logic uses `ndbgetvalue()` for first returned attribute, `ndbsearch()`/`ndbsnext()` for all entries, and prints through a buffered `Biobuf`.

Risks are low; semantics differ subtly among no returned attr, returned attr with `-a`, and returned attr without `-a`.
