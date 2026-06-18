# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/trans2.c

Implements SMB_COM_TRANSACTION2 helpers. Local header/offset helpers mirror `trans.c` but for Trans2 setup words. Exported operations include find-first/find-next directory enumeration, NT and standard path metadata queries, path metadata updates, file length update by handle, filesystem volume/size queries, and DFS referral retrieval.

Directory parsing fills `FInfo` records, including timestamps, size, attributes, resume key, and filename. It contains compatibility workarounds for Windows lying about directory entry counts and old Win9x needing a delay between find-next requests.

Notable defect: `T2fssizeinfo` checks `if(free)` instead of `if(unused)`, so the free-space output pointer guard is wrong.
