
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/params.c -->
# Research: sources/sync-backup/rsync/params.c

## Purpose
`params.c` is rsync's Windows/INI-like configuration parser, derived from Samba. It tokenizes rsync daemon config files into sections and parameter name/value pairs, handles comments and line continuations, and supports include/merge directives.

## Important APIs, Types, and Functions
- Static parser buffer state: `bufr`, `bSize`, `the_sfunc`, and `the_pfunc`.
- Lexer helpers: `EatWhitespace()`, `EatComment()`, and `Continuation()`.
- Token parsers: `Section()` parses `[section]` names and invokes the section callback; `Parameter()` parses `name = value` lines or directive lines and invokes the parameter callback.
- Include support: `include_config()` handles file or directory includes; `parse_directives()` recognizes `&include` and `&merge`.
- `Parse()` is the main file scanner over blank/comment/section/directive/parameter lines.
- `OpenConfFile()` opens a config file with rsync logging.
- Public entry point `pm_process(char *FileName, BOOL (*sfunc)(char *), BOOL (*pfunc)(char *, char *))`.

## Control Flow
`pm_process()` opens a file, allocates the shared buffer for the outermost call, and calls `Parse()`. `Parse()` reads the first non-newline whitespace-delimited character of each line and dispatches to comment skipping, section parsing, directive parsing, or parameter parsing. `Section()` compresses internal whitespace, supports backslash continuation before the closing bracket, rejects empty names, and calls `sfunc`. `Parameter()` first scans the parameter name until `=` or a directive space/tab after `&`, then scans the value while preserving internal whitespace, stripping CR, trimming trailing whitespace, and supporting backslash continuation. Directives call `include_config()`, which recursively calls `pm_process()` on regular files or sorted `*.conf`/`*.inc` directory entries.

## State and Persistence
The parser uses a single reusable global buffer, growing it in 1024-byte increments. Recursive includes reuse the existing buffer instead of allocating another. Include directives can temporarily notify the section callback with synthetic `]push`, `]reset`, and `]pop` section names when managing globals. The parser itself does not persist config; callbacks own storage.

## Dependencies and Integration Points
It depends on rsync logging/allocation/path helpers, `wildmatch`, `item_list`, directory APIs, and callback implementations elsewhere in rsync daemon configuration handling. `&include` uses `*.conf` and manages global section state; `&merge` uses `*.inc` without global push/pop.

## Risks
The global buffer and callback globals make the parser non-reentrant outside its intended recursive include pattern. Include directory traversal is sorted but can recurse deeply or loop if configs include each other. Regex-free manual parsing must preserve legacy whitespace/continuation behavior. Synthetic section names beginning with `]` are an implicit contract with callback code. Very large config tokens can grow memory without a strict cap.

## Test Signals
Config parser tests should cover comments, blank lines, section whitespace compression, empty/bad sections, parameter whitespace trimming, values containing `=`, `[` and `;`, CR stripping, line continuations, bad lines, missing files, `&include` regular files and directories, sorted directory order, `&merge`, and include recursion failure behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/params.c -->
