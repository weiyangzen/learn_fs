## sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/Dockerfile

This Dockerfile builds the fuzz action image. The normal stage installs QEMU, SSH client, curl, C preprocessor/GCC, and LLVM/Clang 20 tooling from apt.llvm.org; smoke-test mode skips heavy dependencies. The final stage creates a `syzkaller` user, copies syzkaller binaries and `/bin/fuzz-action`, and sets the entrypoint.

Integration is with the fuzz Argo template and diff-fuzz manager code. Risks include external apt key/repository availability, `apt-key` deprecation, large image size, root execution despite creating a user, and smoke-test images lacking runtime dependencies.
