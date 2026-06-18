<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/c/build.sh -->
# sources/security-integrity/libcap/contrib/bug216610/c/build.sh

## Purpose
Cross-build helper for bug216610 ARM and ARM64 `.syso` artifacts.

## Important APIs, Types, And Functions
Invokes `gcc.sh` twice with `GCC=arm-linux-gnueabi-gcc` and `GCC=aarch64-linux-gnu-gcc`.

## Control Flow
Changes to the script directory and compiles `fib.c` into `fib_linux_arm.syso` and `fib_linux_arm64.syso`.

## State And Persistence Behavior
Writes `.syso` files next to the script.

## Dependencies And Integration Points
Run inside the Docker image created for the makefile `arms` target.

## Risks And Edge Cases
Assumes cross compilers are installed and `gcc.sh` can fix generated assembly for both targets.

## Test Signals
Signals are the two expected `.syso` files.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/c/build.sh -->
