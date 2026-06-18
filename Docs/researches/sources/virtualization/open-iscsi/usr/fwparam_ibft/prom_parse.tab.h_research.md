# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.tab.h

Generated Bison parser interface for the firmware parser. It declares token enum values for lexer/parser coordination: bus names, boot devices, IPv4, IQN, OBP parameter/qualifier names, hex tokens, virtual-device tokens, CHOSEN tokens, and filenames.

The semantic value union contains `char str[STR_LEN]` with `STR_LEN` defined as 16384 from the grammar. All grammar tokens and nonterminals carry string data through this buffer.

The header also defines `YYLTYPE` with first/last line and column fields, declares global `yylval` and `yylloc`, and exposes `yyparse(struct ofw_dev *ofwdev)`.

This file is generated from `prom_parse.y` and should be regenerated rather than manually changed.
