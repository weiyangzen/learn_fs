## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_remove.c

Purpose: implements legacy `TREMOVE`, removing the object named by a fid and clunking that fid.

APIs and flow: `_9p_remove` validates fid, initializes op context, checks write access, calls `fsal_remove(pfid->ppentry, pfid->name)`, closes open regular files if needed, frees the fid through a local macro that clears `pentry` and the connection slot, and replies `RREMOVE`.

State/dependencies: mutates namespace, closes file state, and releases fid resources. It relies on `ppentry` and `name` having been set by walk/create flows.

Risks/tests: test removing open files, directories vs files, missing parent/name, close failure after remove, read-only exports, invalid fid, and double-release safety.
