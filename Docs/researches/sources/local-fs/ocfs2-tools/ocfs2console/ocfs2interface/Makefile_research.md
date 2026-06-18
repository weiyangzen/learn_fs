# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/Makefile

Builds and installs the Python package and C extension modules for `ocfs2interface`.

Key outputs:
- `plistmodule.so`
- `gidlemodule.so`
- `ocfs2module.so`
- `o2cbmodule.so`
- Python package files listed in `PYSRC`
- Generated `confdefs.py` from `confdefs.py.in`

Libraries:
- `libocfs2`
- `libo2dlm`
- `libo2cb`
- optional `ldlm_lt` for fsdlm support
- optional `cmap`
- internal or system blkid:
  - if `HAVE_BLKID` is unset, links `ocfs2console/blkid/libblkid-internal.a`
- UUID, com_err, GLib, Python config libs

Notable build flags:
- `CFLAGS += -fPIC`
- Python module flags include `-fno-strict-aliasing`
- GLib CPP flags disable deprecated APIs.

Install behavior:
- Creates `$(pyexecdir)/ocfs2interface`.
- Installs all shared modules, Python sources, and generated Python file.

Notable details:
- `toolbar.py` and `tune.py` are included in package source list even though they are outside this research group.
