# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/dump.c

Debug dump helpers for NBNS messages and raw byte data.

Key functions:
- `nbnsdumpname` prints a NetBIOS name with lower-case base name and hex suffix.
- `nbnsdumpmessagequestion` and `nbnsdumpmessageresource` print typed NBNS question/resource records.
- `nbnsdumpmessage` prints header flags plus all question/answer/ns/additional sections.
- `nbdumpdata` prints hex and ASCII byte dumps in 16-byte rows.

Interactions:
- Used by NetBIOS test/client and diagnostic paths.
- Depends on NBNS constants from `netbios.h`.

Notable details:
- Resource data is printed as contiguous hex bytes.
