# sources/test-tools/fio/oslib/linux-dev-lookup.h

Purpose: declaration for Linux block-device lookup used by blktrace replay.

Important APIs/types: declares `blktrace_lookup_device()`.

Control flow and state: no implementation or state.

Dependencies and integration: paired with `linux-dev-lookup.c`; consumers pass a mutable search path buffer and target major/minor.

Risks: the API contract does not expose the required size of `path`, which is important because the implementation copies paths into it.

Test signals: compile consumers and run replay lookup scenarios.
