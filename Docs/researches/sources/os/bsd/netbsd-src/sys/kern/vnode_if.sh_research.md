# File Research: sources/os/bsd/netbsd-src/sys/kern/vnode_if.sh

Read completely: 840 lines.

Generates NetBSD vnode operation front-end source and headers from `vnode_if.src`.

Generated outputs:
- `vnode_if.c`
- `../sys/vnode_if.h`
- `../rump/librump/rumpvfs/rumpvnode_if.c`
- `../rump/include/rump/rumpvnode_if.h`

Parser and input contract:
- Requires one source file argument.
- Extracts the source RCS ID from the first line and embeds both source/script IDs in generated warnings.
- Preprocesses input with `sed` to separate pointer stars from names and replace semicolons with spaces.
- An embedded awk parser recognizes operation blocks beginning with `vop_` and ending with `}`.
- Supports directives `VERSION`, `FSTRANS=`, `PRE=`, `POST=`, and `CONTEXT`.
- Supports argument annotations `LOCKED=EXCL`, `LOCKED=YES`, `LOCKED=NO`, `WILLRELE`, `WILLPUT`, and `WILLMAKE`.

Header generation:
- Emits descriptor offsets, operation argument structures, descriptor declarations, and function prototypes.
- Starts operation offsets at 1 so the default operation is offset 0.
- Emits `VNODE_OPS_COUNT` for kernel headers.
- Rump headers use portable type substitutions for selected kernel types.

C generation:
- Emits common kernel wrapper support for MPSAFE handling, fstrans handling, lockdebug assertions, and kqueue post hooks.
- Emits descriptor offset arrays and `struct vnodeop_desc` objects for each operation.
- Emits normal kernel wrappers that package arguments and call `VCALL`.
- Emits rump wrappers that call the kernel-facing `VOP_*` under `rump_schedule()`/`rump_unschedule()`.
- Emits `vfs_op_descs[]` for the normal kernel output.

Risks and notes:
- The generator relies on awk extensions and detects whether `toupper()` exists, otherwise shelling out to `tr`.
- The parser is whitespace-sensitive after custom sed preprocessing.
- Context fields are only accepted after `PRE` and `POST` handlers and must appear at the end of an argument structure.
- Rump type substitutions are explicitly described as a workaround for non-portable kernel types.
