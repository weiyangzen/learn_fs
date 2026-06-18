# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSFVec.hh

Purpose: defines `XrdOucSFVec`, a compact sendfile vector entry for mixed file-descriptor and memory-buffer output segments.

Important APIs, types, and functions: the struct contains a union of `buffer` and `offset`, plus `sendsz`, `fdnum`, and enum constant `sfMax = 16`. A negative `fdnum` means the union is interpreted as a memory buffer pointer; otherwise it is a file offset for the descriptor.

Control flow: there is no function flow. Callers build an array of up to `sfMax` entries and pass it to sendfile-style code that chooses between file and memory segments based on `fdnum`.

State and persistence: state is transient caller-owned memory. No allocation, locking, or persistence exists.

Dependencies and integration points: depends on `<unistd.h>` for `off_t` and integrates with xrd, sfs, ofs, and oss components that need scatter/gather sendfile descriptions.

Risks and test signals: the union requires consumers to obey the `fdnum` convention exactly. `sendsz` is an `int`, so large fragments must be split. Tests should cover mixed buffer/file vectors, maximum element count, zero-length elements, and correct interpretation when `fdnum < 0`.
