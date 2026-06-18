# File Research: sources/os/plan9/9front/sys/src/cmd/test/patch/header.in

This is a numeric fixture for patch header parsing tests.

Contents:
- Identical numeric sequence to `basic.in`.
- 93 lines of small decimal numbers with deliberate repeats and gaps.

Purpose:
- Provides stable input for testing patch behavior involving headers while keeping file content simple.

Risk notes:
- Exact duplication with `basic.in` is likely intentional for test isolation.
