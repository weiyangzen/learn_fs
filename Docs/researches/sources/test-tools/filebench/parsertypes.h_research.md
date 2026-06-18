<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/parsertypes.h -->
# sources/test-tools/filebench/parsertypes.h

Purpose: defines parser-side data structures passed from yacc grammar productions to command execution callbacks.

Important APIs/types: `list_t` stores string/integer AVD pairs for quoted/string parameter lists. `attr_t` stores an attribute token id, linked-list pointer, AVD value, or object pointer such as a probability table. `cmd_t` stores callback pointer, command/entity names, quantities, nested command lists, attribute lists, and parameter lists. `fs_u` is a small semantic-value union. `pidlist_t` tracks child process fd/pid pairs. `cmdfunc` names command callback signatures. It declares lexer buffer switch helpers.

Control flow contract: grammar productions allocate these nodes, link them in source order, and command callbacks traverse them to create Filebench runtime objects.

State/persistence: these structures are mostly transient heap parser state, while their AVDs may reference shared variables or shared-memory allocations.

Dependencies/integration: includes `filebench.h` for `avd_t` and project types; token ids come from grammar definitions.

Risks: generic fields make ownership unclear. Some command nodes are freed at top level, but nested lists/attrs/strings have partial cleanup, so parser lifetime assumes short process runs. Attribute ids are plain ints, so misuse is detected only by command-specific logic.

Test signals: parser memory/debug tests for nested process/thread/flowop definitions, composite local variables, parameter lists, and random probability-table objects.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/parsertypes.h -->
