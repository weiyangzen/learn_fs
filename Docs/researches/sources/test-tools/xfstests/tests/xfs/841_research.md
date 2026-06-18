<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/841 -->
# sources/test-tools/xfstests/tests/xfs/841

Purpose: verifies bit-for-bit reproducible XFS image creation when `mkfs.xfs` is supplied fixed reproducibility inputs.

Important APIs, types, and functions: checks `-m uuid=`, `-p` population, `SOURCE_DATE_EPOCH`, and `DETERMINISTIC_SEED`; creates a proto directory with fsstress plus fifo, socket, block, and character device entries; hashes images with sha256sum.

Control flow: build a prototype tree, create three fresh 512 MiB images with fixed UUID and epoch, mount each image to compare the tree, collect hashes, and require all hashes to match.

State and persistence behavior: temporary prototype, mount directory, and image file live under `$TEST_DIR` and are removed by cleanup.

Dependencies and integration points: depends on mkfs reproducibility support, fsstress, af_unix helper, mount/unmount helpers, and root privileges for special device nodes when available.

Risks and test signals: special files may be skipped if creation fails, but reproducibility still depends on deterministic metadata. The main signal is `All filesystem images are identical.`
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/841 -->
