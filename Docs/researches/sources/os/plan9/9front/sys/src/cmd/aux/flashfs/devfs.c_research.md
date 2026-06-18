# File Research: sources/os/plan9/9front/sys/src/cmd/aux/flashfs/devfs.c

Role: Flashfs data backend for either a real flash device or a plain file.

Initialization:
- `initdata` opens the data path. If a sibling `<path>ctl` exists, it treats the target as a flash device and reads geometry from the control file.
- If no control file exists, it treats the target as a plain file, infers `nsects` from file length when needed, defaults sector size to 512, and allocates an all-0xff erase buffer.

Operations:
- `clearsect` erases by writing all 0xff bytes for plain files or by writing an `erase` command to the flash control file.
- `readdata` performs checked `pread`.
- `writedata` performs checked `pwrite`, optionally returning failure instead of fatal error when the `err` flag is set.

Assumptions:
- Real flash control files report at least seven geometry fields; field 5 is sector count and field 6 is sector size.
