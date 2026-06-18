# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_scrub.h

`iter_scrub.h` declares the DNS message scrubbing entry point `scrub_message()`. The function takes the original packet buffer, parsed message, original query, active delegation/zone name, regional allocator, module environment, query state for EDE error information, and iterator environment.

The API promises to mutate the parsed message by removing useless or malicious data while leaving the packet buffer unchanged. It returns false when the message is unusable.

This header exposes only the high-level scrubber; all normalization, glue marking, DNAME/CNAME synthesis, and poison filtering helpers remain private to `iter_scrub.c`.
