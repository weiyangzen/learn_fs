# File Research: sources/os/plan9/9front/sys/src/cmd/vac/dat.h

`dat.h` defines internal metadata block structures for the vac archive filesystem tools. It sets constants for maximum block size, estimated directory-entry bytes, block fullness threshold, flush size, and dirty percentage.

`MetaEntry` points at an entry payload and size. `MetaBlock` tracks allocated/used/free metadata block space, index table capacity/use, an `unbotch` flag, and the backing buffer. `VacDirEnum` stores directory enumeration state over a `VacFile`.
