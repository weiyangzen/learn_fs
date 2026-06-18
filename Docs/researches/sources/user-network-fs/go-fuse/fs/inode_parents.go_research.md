# sources/user-network-fs/go-fuse/fs/inode_parents.go

Purpose: tracks one or more parent directory/name links for an inode, supporting hard links and path reconstruction.

Important types/functions: `inodeParents` stores a `newest` parent plus an `other` map. `add` keeps the most recently added parent as newest and avoids duplicates; `get` returns newest; `all` returns every known parent; `delete` removes a parent and promotes an arbitrary other parent when needed; `clear` removes all parents; `count` reports cardinality. `parentData` holds name and parent inode.

Control flow/state: no internal locking; callers must hold appropriate inode locks.

Integration/risks: used by `Inode.Path`, child set/delete, directory single-parent enforcement, and removal cascading. Risks include nondeterministic parent promotion from map iteration and caller lock misuse. `inode_parents_test.go` covers counts and newest behavior.
