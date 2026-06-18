# File Research: sources/os/plan9/9front/sys/src/cmd/upas/spf/macro.c

`macro.c` expands SPF macro strings. It supports sender/local/domain/IP/PTR/version/helo macros, digit truncation, reverse ordering, delimiter selection, percent escapes, and defaults for unset sender/domain/helo/IP values.

IPv6 `%{i}` expansion emits nibble-dot form; `%{p}` performs reverse lookup validation via PTR plus forward address confirmation. The macro engine writes into bounded internal buffers and returns a newly allocated string, or nil for malformed macro syntax.

The implementation includes helper chopping/reversing logic that follows SPF macro field manipulation rules closely enough for local evaluation and the included testsuite.
