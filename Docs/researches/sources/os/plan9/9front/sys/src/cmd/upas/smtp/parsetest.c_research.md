# File Research: sources/os/plan9/9front/sys/src/cmd/upas/smtp/parsetest.c

`parsetest` is a diagnostic driver for the RFC 822 header parser. It reads up to 128 KiB from each file argument, calls `yyinit()`/`yyparse()`, prints reconstructed parsed headers, frees `Field`/`Node` structures, and flushes output.

It is useful for validating parser normalization and memory cleanup without involving SMTP delivery.
