# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/fetch.c

FETCH response implementation for `imap4d`. It maps requested attributes to message flags, UIDs, internal dates, envelopes, RFC822 sizes, BODY, BODYSTRUCTURE, and BODY section literals, and implicitly marks messages seen for body-reading operations.

Body section handling maps IMAP sections to upas/fs files: raw headers, raw bodies, MIME headers, or combined body/header views. It supports partial fetches, header field selection/inversion, multipart/bodystructure recursion, message/rfc822 nesting, MIME parameters, addresses, and CRLF normalization of body literals.
