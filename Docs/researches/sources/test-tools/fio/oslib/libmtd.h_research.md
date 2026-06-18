# sources/test-tools/fio/oslib/libmtd.h

Purpose: public API and data model for fio's imported MTD library.

Important APIs/types: defines `MTD_NAME_MAX`, `MTD_TYPE_MAX`, opaque `libmtd_t`, `struct mtd_info`, and `struct mtd_dev_info`. Declares discovery APIs, eraseblock lock/unlock/erase/region/lock-status APIs, bad-block APIs, raw and OOB read/write APIs, image-write helper, and node probing.

Control flow and state: no implementation; it defines the contract implemented by `libmtd.c` and `libmtd_legacy.c`. The API passes an opaque library descriptor plus caller-owned `mtd_dev_info` structs and open file descriptors.

Dependencies and integration: C++ compatible extern block; includes `<stdint.h>` and forward-declares `struct region_info_user`. Consumers are expected to include Linux MTD headers where concrete ioctl structs are needed.

Risks: many APIs are destructive and require a valid MTD fd plus accurate eraseblock geometry. The public comments are important because misuse can erase or mark bad blocks. `mtd_lock()`/`mtd_unlock()` comments mention a descriptor parameter that is not actually in the signature.

Test signals: compile consumers against the header and run integration tests for each operation on controlled MTD devices.
