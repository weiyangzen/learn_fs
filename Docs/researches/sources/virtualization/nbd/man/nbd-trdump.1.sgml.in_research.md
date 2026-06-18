# File Research: sources/virtualization/nbd/man/nbd-trdump.1.sgml.in

DocBook manpage template for `nbd-trdump(1)`.

It documents a filter that reads an `nbd-server` transaction log from stdin and writes human-readable output to stdout. The log comes from the server `transactionlog` configuration directive.

The output legend identifies request/reply/structured-reply markers and fields for cookie, command, offset, length, error, structured reply type, and structured reply flags.
