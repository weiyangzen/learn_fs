# sources/security-integrity/selinux/libsepol/cil/src/cil_parser.c

## Purpose
`cil_parser.c` is a hand-written parser that converts lexer tokens into a raw parenthesized CIL parse tree. It also records source-path and high-level-language line-marker information as synthetic source-info nodes.

## Important APIs, Types, And Functions
The public function is `cil_parser(const char *path, char *buffer, uint32_t size, struct cil_tree **parse_tree)`. Important helpers include `push_hll_info`, `pop_hll_info`, `create_node`, `insert_node`, `add_hll_linemark`, and `add_cil_path`. `CIL_PARSER_MAX_EXPR_DEPTH` limits parenthesis and line-marker nesting.

## Control Flow
The parser initializes the lexer on a caller-provided buffer, adds a source-info node for the CIL path, then loops over tokens. `OPAREN` creates a child parse node and descends. `CPAREN` ascends and checks balance. `SYMBOL` and `QSTRING` create leaf nodes under the current expression, with strings interned through the string pool. Comments are consumed until newline or EOF. HLL line markers create nested source-info expressions and maintain a stack of previous offsets/expansion mode.

## State And Persistence Behavior
The function mutates the caller-provided parse tree by appending nodes. Node data strings are interned through `cil_strpool_add`; quoted strings are stripped in place before interning. HLL state is local stack data, and scanner state is destroyed on both success and error.

## Dependencies And Integration Points
It depends on the lexer, CIL tree, stack, string pool, memory wrappers, and logging. Public loading code in `cil.c` calls it before AST building. Later diagnostics use line and `hll_offset` fields filled here.

## Risks And Edge Cases
The parser performs structural validation only; semantic validation is later. It rejects symbols outside parentheses, unmatched parentheses, unknown tokens, invalid HLL markers, and nesting over 4096. Error exits leave any already appended parse nodes in the tree for the caller/database cleanup path. Quoted string mutation requires mutable input buffers.

## Test Signals
Unit tests should cover valid parse-tree shape, comments, quoted strings, top-level symbol rejection, unmatched parentheses, depth limits, HLL start/end/expand behavior, EOF after comments, and source path source-info insertion.
