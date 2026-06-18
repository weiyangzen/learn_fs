# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbnsconv.c

Owns NBNS message allocation, list management, decoding, and encoding.

Key functions:
- `nbnsmessagefree`, `questionfree`, and `resourcefree` free full message graphs.
- `nbnsmessagequestionnew` and `nbnsmessageresourcenew` allocate records and copy names/rdata.
- `nbnsconvM2S` parses the NBNS header, flags, questions, and resource sections.
- `nbnsconvS2M` writes header counts, flags, questions, and resource sections.
- `resourcedecode` and `resourceencode` handle common resource body parsing.

Interactions:
- Underpins all NBNS request/response code.

Notable details:
- On decode failure, partially built messages are freed through `nbnsmessagefree`.
- There is a likely typo in `resourcedecode`: after `r->rdata = malloc(...)`, it checks `if (r == nil)` rather than `if (r->rdata == nil)`.
