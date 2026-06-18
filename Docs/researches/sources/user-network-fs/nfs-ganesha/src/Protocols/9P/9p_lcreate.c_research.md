## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_lcreate.c

Purpose: implements 9P2000.L file create-and-open.

APIs and flow: `_9p_lcreate` validates a directory fid, checks write export permissions, copies the child name, translates Linux open flags to FSAL flags/share access, prepares mode/group/optional truncate attributes, selects `FSAL_EXCLUSIVE_9P` for exclusive creates, calls `fsal_open2`, releases attrs, replaces the fid's object with the new file, sets qid, marks `opens = 1`, holds an active parent reference, and returns qid/iounit.

State/dependencies: mutates the existing fid from directory to opened file, owns FSAL state and parent refs, and depends on FSAL open/create semantics.

Risks/tests: failure after parent ref/object replacement would be dangerous, so the code orders irreversible updates after successful FSAL calls. Test guarded/exclusive/truncate flags, long names, read-only exports, parent reference balancing, and close-on-clunk.
