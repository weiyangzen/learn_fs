# sources/test-tools/xfstests/tests/ocfs2/001


Purpose: OCFS2 reflink regression test ensuring inline-data files can participate correctly in clone/reflink operations with regular files and other inline files.


Important APIs, helpers, and commands: Imports `common/reflink`; uses `_scratch_mkfs --fs-features=local,unwritten,refcount,inline-data`, `tunefs.ocfs2 --query`, `_cp_reflink`, `_reflink_range`, and md5sum.
 It imports `./common/filter`, `./common/preamble`, `./common/reflink`.
 Capability gates include `_require_cp_reflink`, `_require_scratch_reflink`.



Control flow, state, dependencies, risks, and test signals: It formats OCFS2 with inline-data/refcount features, verifies inline-data support, creates regular and small inline files, remounts, reflinks a large file into small files at start/past EOF, reflinks inline data into regular and inline targets, remounts, and md5sums all files. State includes inline-data inodes, refcounted extents, and cloned file contents. Dependencies are OCFS2 tools and reflink support. Risks are feature availability and clone semantics across inline/regular conversion. Signal is stable md5sum output. Source size is 56 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
