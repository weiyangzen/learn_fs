# sources/security-integrity/ecryptfs-utils/src/libecryptfs/module_mgr.c

## Purpose
Builds and processes the eCryptfs mount-option decision graph. It connects key-module selection, existing signatures, cipher/key-size selection, kernel-version-gated features, filename encryption, and repeated key handling into the generic graph engine.

## Important APIs, types, and functions
- Static `param_node` definitions model options such as `sig`, `key`, `ecryptfs_cipher`, `ecryptfs_key_bytes`, passthrough, HMAC, xattr metadata, encrypted view, and FNEK signature.
- Transition callbacks push mount options or mutate graph edges.
- `init_ecryptfs_cipher_param_node`, `init_ecryptfs_key_bytes_param_node`, and `fill_in_decision_graph_based_on_version_support` build graph branches.
- `ecryptfs_process_decision_graph` is the main mount option processor.
- `ecryptfs_process_key_gen_decision_graph` drives key-generation subgraphs.

## Control flow
Mount processing registers key modules, allows duplicate `key` options, asks each module for a parameter subgraph or builds a linear one, and attaches those transitions to the key selector. It fills the rest of the graph when all mount options are requested, otherwise routes key-module-only processing to a dummy exit. It parses rc-file and option-string name/value pairs, merges them with CLI precedence and allowed duplicates, stores the merged list in `ctx`, then evaluates from `root_param_node`. Existing `sig=` skips key selection; absent or `NULL` signatures route into key-module selection. The `another_key` node loops back to key selection when unprocessed key options remain, enabling multiple keys.

## State and persistence behavior
Mutates static graph nodes, suggested values, transition counts, and transition next pointers. It allocates allowed-duplicate list entries and graph transition strings. External persistent effects come from key-module subgraphs adding keys to the kernel keyring and from reading `~/.ecryptfsrc`.

## Dependencies and integration points
Integrates option parsing, key-module registration, decision graph evaluation, sysfs feature checks, and keyring insertion. It is called by mount helper flows and depends on `ecryptfs_supports_*` functions from `sysfs.c`.

## Risks and edge cases
Static nodes make repeated calls vulnerable to stale transition counts, suggested values, and next-token mutations. `init_ecryptfs_cipher_param_node` and key-byte initialization append without obvious reset. `tf_ecryptfs_cipher` removes min/max key-byte pseudo-options while iterating a stack and mixes ownership of list values. Feature graph shape depends on kernel version flags, so old kernels skip prompts/options silently. Boolean parsing accepts only lowercase `y/yes/n/no`.

## Test signals
Integration tests should process option strings for existing signature mounts, passphrase key-module mounts, multiple keys, cipher/key-byte min/max constraints, filename encryption suggested FNEK signature, and version masks with and without passthrough/HMAC/xattr/FNEK support. Repeated invocations in one process are especially important.
