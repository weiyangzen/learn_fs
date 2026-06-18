# sources/user-network-fs/nfs-ganesha/src/test/CMakeLists.txt

Purpose: declares small support/unit test executables for AVL, hash/AVL, glist, URL regex, and CIDR behavior.

Important APIs, types, and functions: CMake targets are `test_avl`, `test_mh_avl`, `test_glist`, `test_url_regex`, and `test_cidr`. CUnit-based targets are guarded by `USE_CUNIT`.

Control flow: when `USE_CUNIT` is enabled, AVL tests are built `EXCLUDE_FROM_ALL` and linked with `ganesha_nfsd` and threads. Other tests are always declared `EXCLUDE_FROM_ALL`; CIDR links only `ganesha_nfsd`.

State and persistence: no runtime state; build graph only.

Dependencies and integration points: depends on `ganesha_nfsd`, CUnit, thread libraries, and support sources such as `../support/murmur3.c`.

Risks: `EXCLUDE_FROM_ALL` means these tests will not build in default builds. Some test executables do not integrate with CTest here, so build declaration alone may not ensure automated execution.

Test signals: enables manual or CI-driven focused checks of foundational containers and parsers once explicit build/run steps include these targets.
