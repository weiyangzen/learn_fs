# File Research: sources/virtualization/nbd/netdb-compat.h

## Purpose
Provides a compatibility definition for `AI_NUMERICSERV` on platforms whose `<netdb.h>` does not define it.

## Main Contents
If `AI_NUMERICSERV` is missing, defines it as `0`, allowing code that sets the flag in `addrinfo.ai_flags` to compile while effectively ignoring the optimization.

## Dependencies
Intended to be included after or alongside networking headers that may define `AI_NUMERICSERV`.

## Risks and Notes
Using zero is acceptable because `AI_NUMERICSERV` is a flag used to avoid service-name resolution; ignoring it changes performance/lookup strictness rather than protocol data layout.
