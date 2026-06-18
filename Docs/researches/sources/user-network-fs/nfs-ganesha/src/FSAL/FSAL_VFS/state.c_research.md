# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/state.c

Purpose: this file provides VFS state-handle storage for builds using `VFS_NO_MDCACHE`, keyed by object handle bytes.

Important functions: `vfs_state_cmpf` compares `gsh_buffdesc` keys by length then bytes. `vfs_state_lookup` searches the AVL tree. `vfs_state_init` initializes the global tree. `vfs_state_release` removes and frees an entry by key. `vfs_state_locate` maps an object to a persistent `state_hdl`, creating a `vfs_state_entry` if needed and initializing it with `state_hdl_init`.

Control flow and state: a process-global AVL tree maps file-handle keys to `state_hdl` objects. `vfs_state_locate` always updates `ostate.file.obj` to the current object pointer, allowing reconstructed handles to reuse state. `free_vfs_fsal_obj_handle` releases state entries for regular files.

Dependencies and integration points: uses Ganesha SAL state structures, AVL helpers, object `handle_to_key`, and VFS handle release paths.

Risks: the tree is global and this file does not show explicit locking; correctness depends on surrounding serialization or build-mode assumptions. Keys point at handle memory (`gsh_buffdesc`) rather than deep-copying bytes, so lifetime must be tied to object handles. Race handling after `avltree_insert` frees the loser entry but still depends on safe concurrent tree access.

Test signals: locate/release cycles for duplicate handles, reconstructed handles, concurrent state lookup if supported, regular-file handle release, and no-MDCACHE builds.
