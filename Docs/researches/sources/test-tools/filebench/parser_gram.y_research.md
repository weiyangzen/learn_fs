<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/parser_gram.y -->
# sources/test-tools/filebench/parser_gram.y

Purpose: defines the yacc grammar, command callbacks, option parsing, and `main()` entry point for Filebench's Workload Model Language interpreter.

Important APIs/functions: grammar rules build `cmd_t`, `attr_t`, `list_t`, and `probtabent_t` structures for commands including `define`, `create`, `run`, `psrun`, `set`, `eventgen`, `enable multi`, `domultisync`, `system`, `echo`, `sleep`, `list`, `version`, and `quit`. Callback functions instantiate procflows, threadflows, flowops, composite flowops, files/filesets, random variables, and custom variables. `parse_options()` selects help, master, worker, or custom-variable listing modes; `master_mode()` initializes IPC, flowops, eventgen, cvars, and invokes `yyparse()`; `worker_mode()` attaches to shared memory and executes a procflow.

Control flow: lexer tokens feed grammar productions. Completed commands execute immediately in the top-level `commands` rule. Master mode parses WML and typically exits through `run`/`psrun` shutdown; worker mode is invoked by master with private `-a/-s/-m/-i` parameters. Composite flowops are defined as flowop trees with local variable attributes propagated into inner flowops.

State/persistence: command and attribute nodes are heap allocated during parsing; durable benchmark objects are allocated in shared memory through fileset/procflow/threadflow/flowop/var/cvar APIs. `execname` stores the executable path for worker exec. Global `filebench_shm` records run modes, debug flags, lathist enablement, and script name.

Dependencies/integration: ties together almost every subsystem: parser lexer, variables/AVDs, filesets, flowops, procflows, eventgen, stats, IPC, cvar libraries, ASLR control, multi-client sync, and platform resource setup.

Risks: commands execute while parsing, so syntax accepted before a later parse error may already mutate shared state. Attribute lookup returns the last matching attribute without duplicate diagnostics. Many parser errors call `filebench_shutdown(1)`. `system` intentionally executes shell commands from WML. Composite/local variable handling depends on shared local-variable list manipulation.

Test signals: parser tests for every command form and attribute; malformed WML recovery; master/worker command-line modes; composite flowop local variables; random/cvar definitions; run modes (`timeout`, `firstdone`, `alldone`, `nousestats`); periodic stats; and no-run warning behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/parser_gram.y -->
