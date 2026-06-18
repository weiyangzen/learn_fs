## sources/security-integrity/audit-userspace/audisp/plugins/ids/avl.h

Purpose: intrusive AVL tree types and APIs for IDS models.

It defines `avl_t`, `avl_tree_t`, iterator stack, maximum height, and public insert/remove/search/traverse/iterator/intersection functions. State is caller-owned, with `avl_t` embedded in containing records. Dependencies are compiler warning attributes. Risks include callers needing stable node memory and a comparison function consistent over node lifetime. Test signal is all IDS indexes that embed AVL nodes.
