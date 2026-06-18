# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/message.c

`message.c` owns message allocation, reading, RFC 822 header normalization, sender/date extraction, large-message spillover, and output formatting. It keeps the first `VMLIMIT` bytes in memory and stores additional data in an ORCLOSE temp file, rejecting above `MSGLIMIT`.

For incoming rmail, `m_read()` parses Unix `From` lines, remote system chains, and dates using regexes. `rfc822cruft()` invokes the SMTP RFC 822 parser to discover headers, count `Received:`, mark bulk mail, preserve subject/from/reply-to metadata, and rewrite equivalent bang systems in address nodes.

Output functions print mailbox `From ` lines, synthesize `Date`, MIME UTF-8 headers, `From`, and `To` when absent, and choose escaped or raw body output. `m_get()` abstracts reading across memory and temp-file segments.
