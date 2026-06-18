# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/model.h

Purpose: Defines data-model constants and helper macros for handling 32-bit vs 64-bit user data structures in the kernel.

Key definitions:
- `DATAMODEL_ILP32`, `DATAMODEL_LP64`, `DATAMODEL_NATIVE`, `DATAMODEL_MASK`, `DATAMODEL_NONE`.
- `model_t`.

Kernel LP64 helper macros:
- `STRUCT_HANDLE`, `STRUCT_DECL`, `STRUCT_SET_HANDLE`, `STRUCT_INIT`.
- `STRUCT_SIZE`, `STRUCT_FADDR`, `STRUCT_FGET`, `STRUCT_FGETP`, `STRUCT_FSET`, `STRUCT_FSETP`, `STRUCT_BUF`.
- `SIZEOF_PTR`, `SIZEOF_STRUCT`.

Data-model APIs:
- `lwp_getdatamodel()`
- `get_udatamodel()`

Important detail: On 64-bit kernels the macros create a dual 32/64 pointer view over the same logical structure; on 32-bit kernels they collapse to native-only behavior.

Relevance to subset A: Critical syscall/ioctl ABI support. Many filesystem, mount, memory, and device structs in this group have 32-bit variants that depend on this model.
