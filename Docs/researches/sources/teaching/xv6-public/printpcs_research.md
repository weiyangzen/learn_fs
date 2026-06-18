# File Research: sources/teaching/xv6-public/printpcs

Shell helper for decoding panic program-counter lists.

Behavior:
- Searches for an i386-capable `addr2line`.
- Enables supported pretty-printing flags parsed from `addr2line -h`.
- Runs `addr2line` against the `kernel` image with supplied addresses.

Used for debugging panic call stacks printed by `panic`.
