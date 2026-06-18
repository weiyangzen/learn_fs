# sources/test-tools/syzkaller/pkg/declextract/typing.go

Purpose: `typing.go` performs resource/type inference over extracted data-flow facts. It refines syscall arguments, returns, struct fields, ioctl variants, and interface scope calculations.

Important APIs/types/functions: `typingNode` represents a graph node with bidirectional flows. `processTypingFacts` builds the graph. `canonicalNode` and `TypingEntity.ID` normalize local, field, argument, return, and global-address entities. Public inference entry points are `inferReturnType`, `inferArgType`, `inferFieldType`, `inferCommandVariants`, and `inferArgFlow`. `inferContext.walk`, `relevantScope`, and `refineFieldType` perform graph traversal and application.

Control flow and state: extracted scope facts become edges in per-function or global maps. Inference walks both from and to a node, looking for known resource producers or consumers from `flowResources`, respecting command-specific scopes where needed. Shorter paths win, with lexical tie-breaking for determinism. Command variants are collected from switch scopes reachable from an argument. Traversal depth is capped to limit false positives.

Dependencies and integration: the file relies on `FunctionScope` facts from `entity.go`, function lookup in `interface.go`, and generated field types from `declextract.go`. It feeds `processSyscalls`, `processStructs`, `createIoctls`, and LOC relevance.

Risks: the comments list many known limitations: incomplete resource dictionaries, missing SSA, possible false fd return inference, no const/unused-arg inference, and coarse ignore lists for noisy functions/files/structs. The graph is mutable and unguarded, but used during single-threaded generation. No direct tests are included.
