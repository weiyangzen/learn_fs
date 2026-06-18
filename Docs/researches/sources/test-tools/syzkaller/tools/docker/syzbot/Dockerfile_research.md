<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/syzbot/Dockerfile -->
# sources/test-tools/syzkaller/tools/docker/syzbot/Dockerfile

## Purpose

syzbot command execution container image.

## Important APIs, Types, and Functions

Static strace build stage; final Debian image with kernel deps, cross compilers, LLVM 22/clang-15, QEMU, Rust, gcloud, bazelisk, syzkaller user, command wrapper.

## Control Flow

Builds strace, installs broad toolchain set, configures alternatives and Cloud Source credential helper, fetches bazelisk dynamically, creates user, copies wrapper.

## State and Persistence Behavior

Container filesystem stores tools and system git config.

## Dependencies and Integration Points

Depends on Debian/LLVM/GitHub/gcloud repos and architecture-specific packages.

## Risks and Edge Cases

Dynamic latest bazelisk harms reproducibility; broad trusted tool install expands supply-chain surface.

## Test Signals

Build image and run `/run-syz-command.sh make presubmit` or representative syzbot commands.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/docker/syzbot/Dockerfile -->
