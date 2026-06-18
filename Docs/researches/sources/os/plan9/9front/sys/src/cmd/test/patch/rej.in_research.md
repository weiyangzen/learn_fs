# File Research: sources/os/plan9/9front/sys/src/cmd/test/patch/rej.in

This is a numeric fixture for patch rejection tests.

Contents:
- 93 lines.
- Similar to `basic.in`, but differs at key locations: includes `16` where the basic fixture has `13`, and ends with repeated `96`.

Purpose:
- Designed to create context mismatches or rejected hunks when applying a patch made for a slightly different input.

Risk notes:
- Fixture value lies in exact differences from sibling `.in` files.
