# sources/test-tools/syzkaller/pkg/mgrconfig/testdata/qemu-example.cfg

Purpose: Comment-heavy QEMU example config fixture used by `TestCanned`.

Important content: Provides target `linux/amd64`, bind-all HTTP address, workdir under testdata, kernel object/source placeholders, testdata image, syzkaller path, procs 4, type `qemu`, and VM config with count, kernel path, CPU, and memory.

Control flow and state: Validates that commented example-style config remains parseable and that QEMU VM raw JSON can be decoded.

Dependencies and integration: Exercises comment handling in config loader, QEMU schema, image path validation, and binary path resolution.

Risks: Contains documentation comments with external URLs and placeholders; test success depends on only fields that completion validates.

Test signals: Guards against breaking the documented example config format.
