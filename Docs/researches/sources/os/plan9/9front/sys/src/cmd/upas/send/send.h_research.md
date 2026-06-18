# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/send.h

`send.h` declares the destination and message data models plus the cross-file API for `upas/send`. `d_status` enumerates every address resolution/delivery state, including pipes, local cats, aliases, auth, loops, bad mailboxes, resources, and `pipeto`.

The `dest` structure carries address, substitutions, parent alias chain, process status, authorization, and batching fields. The `message` structure carries sender/reply/date/body, storage fd, parsed-header flags, MIME/bulk state, boundary, and received count.

The header is the main integration contract between binding, rewriting, local expansion, message formatting, logging, and refusal handling.
