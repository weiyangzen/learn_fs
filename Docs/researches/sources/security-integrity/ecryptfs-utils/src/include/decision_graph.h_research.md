# sources/security-integrity/ecryptfs-utils/src/include/decision_graph.h

Purpose: declares the internal decision-graph structures that drive interactive and option-file mount/key-module configuration.

Important APIs/types: `val_node`, `transition_node`, `param_node`, `prompt_elem`, flags for prompt behavior/validation/defaults/transitions, and functions for adding/dumping graph nodes, setting exits, inserting name/value params, and evaluating parameter trees.

Control flow model: a `param_node` represents a mount option prompt/value; transitions choose next nodes based on values or default matches and may run `trans_func`. `val_node` works as a stack of generated mount options or intermediate values. Return tokens such as `DEFAULT_TOK`, `MOUNT_ERROR`, and `WRONG_VALUE` steer traversal.

State/persistence: graph nodes hold mutable `val`, defaults, suggestions, flags, and transition arrays; no persistence by themselves.

Dependencies/integration: included by key modules and libecryptfs decision graph implementation. It references `ecryptfs_ctx` and name/value pairs.

Risks: fixed-size arrays (`MAX_NUM_MNT_OPT_NAMES`, `MAX_NUM_TRANSITIONS`) can constrain modules. Comments warn structures are shared kernel/userspace width-sensitive, though these decision graph structs are mostly userspace.

Test signals: mount option parsing and key-module decision graph traversal tests.
