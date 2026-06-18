# File Research: sources/virtualization/nvme-cli/ccan/ccan/build_assert/build_assert.h

- Purpose: compile-time assertion helpers.
- Key APIs: `BUILD_ASSERT(cond)` for statement context and `BUILD_ASSERT_OR_ZERO(cond)` for expression context.
- Mechanism: uses invalid char array size to force compile failure when condition is false.
- Use: foundational helper for CCAN type/size checking macros.
