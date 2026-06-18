## sources/test-tools/syzkaller/syz-cluster/workflow/retest/Dockerfile

This Dockerfile packages the retest action. The normal stage installs QEMU, SSH client, curl, compiler tools, and LLVM/Clang 20; smoke-test mode skips heavy dependencies. The final image creates a `syzkaller` user, copies syzkaller binaries plus `/bin/retest-action`, and sets the entrypoint.

Integration is with retest workflow template. Risks mirror fuzz action images: external apt repository dependency, large image, root execution by default, and smoke-test dependency mismatch.
