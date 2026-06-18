# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_lex.c

Generated Flex scanner for Open Firmware / OBP iSCSI boot-path parsing. It is generated from `prom_lex.l` using Flex 2.5.35 and includes the full scanner runtime: buffer management, `yy_scan_*` helpers, restart/switch APIs, global scanner state, token text storage, and allocation wrappers.

Project-specific behavior is embedded from `prom_lex.l`. It includes `prom_parse.h`, fills `yylval.str` with the matched token text through `upval(d)`, updates `yylloc` columns, and returns parser tokens for Open Firmware path components.

Recognized token classes include boot property names (`bootpath`, `bootargs`, `iscsi-bootargs`, `nas-bootdevice`), virtual device components (`vdevice`, `gscsi`, `dev`, `rawio`), bus names, boot devices, IPv4 addresses, IQNs, OBP qualifiers, OBP parameters, short and long hex strings, and escaped filenames. Whitespace is consumed while preserving column progress. Any unmatched single character is returned literally, which lets the Bison grammar consume delimiters such as `/`, `@`, `,`, `:`, and `=`.

Important implementation detail: scanner output uses `%option array`, so `yytext` is a fixed array with `YYLMAX` defaulting to 8192. Token transfer uses `strcat(yylval.str, yytext)` after clearing the destination first. The parser union buffer is larger (`STR_LEN` 16384), so scanner token size is the tighter bound.

This file should normally be regenerated from `prom_lex.l`, not edited directly. Behavioral changes belong in the `.l` source.
