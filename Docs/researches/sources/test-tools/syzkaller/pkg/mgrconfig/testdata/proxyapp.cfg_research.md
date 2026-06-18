# sources/test-tools/syzkaller/pkg/mgrconfig/testdata/proxyapp.cfg

Purpose: Canned proxyapp manager config fixture for `TestCanned`.

Important content: Defines target `linux/amd64`, workdir, syzkaller path, HTTP address, type `proxyapp`, VM command and nested proxyapp config (`count`, kernel tarball, manager host), procs 32, disabled `clock_settime`, and `reproduce: false`.

Control flow and state: Loaded through `LoadFile`, then raw VM config is parsed into `proxyapp.Config`.

Dependencies and integration: Exercises proxyapp VM schema and a high-procs config with reproduction disabled.

Risks: Uses placeholder paths that are accepted by schema parsing but may not represent runnable local state. Does not cover SSH/image fields.

Test signals: Positive fixture for proxyapp config compatibility and disabled-syscall parsing.
