# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/filter.y

This is the yacc grammar and lexer for snoopy filter expressions. It builds `Filter` trees using `newfilter`.

The grammar supports bare words, equality, inequality via `!=`, protocol/function-style grouping `WORD(expr)`, parentheses, logical OR/AND with both symbolic and doubled operators, and unary negation.

`yyinit` sets the input string. `yylex` skips whitespace, tokenizes words and punctuation/operators, allocates a filter node for each token, and stores word strings with `strdup`. `yyerror` terminates with `sysfatal`.

The grammar encodes inequality as a negated equality subtree rather than a separate comparison primitive.
