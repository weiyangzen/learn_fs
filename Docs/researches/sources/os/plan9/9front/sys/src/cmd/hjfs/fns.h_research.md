# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/fns.h

Declares the internal `hjfs` API.

Key points:
- Memory helpers: `emalloc`, `erealloc`, `estrdup`.
- Buffer/device helpers: `bufinit`, `getbuf`, `putbuf`, `sync`, `pack`, `unpack`, `newdev`.
- Filesystem core: `initfs`, `getdent`, `getfree`, `putfree`, `getblk`, `trunc`, `delete`, `chref`, `newentry`, `findentry`.
- Channel/9P operations: `chanattach`, `chanclone`, `chanwalk`, `chancreat`, `chanopen`, `chanwrite`, `chanread`, `chanstat`, `chanwstat`, `chanclunk`, `chanremove`.
- Identity and auth: `permcheck`, `uid2name`, `name2uid`, `usersload`, `userssave`, `ingroup`, `writeusers`, `readusers`.
- Server/ops: `start9p`, `initcons`, `shutdown`, `fsdump`, `willmodify`, `workerinit`.
- Location management: `chbegin`, `chend`, `newqid`, `getloc`, `haveloc`, `cloneloc`, `putloc`.
- Validation/debug: `namevalid`, `modified`, `dprint`.
- Declares `dprint` vararg checking.

Dependencies and interactions:
- Included by all `hjfs` implementation files.
- Serves as the module boundary between the files in this group and omitted core files.

Research relevance:
- Function map for the `hjfs` filesystem implementation, showing the subsystems not all present in this work item.
