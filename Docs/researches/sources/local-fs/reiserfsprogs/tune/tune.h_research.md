# File Research: sources/local-fs/reiserfsprogs/tune/tune.h

Shared header for `reiserfstune`.

Major responsibilities:
- Includes configuration, I/O, misc helpers, ReiserFS core library, and version banner definitions.
- Conditionally includes `uuid/uuid.h`.
- Defines option bit masks used by `tune.c`: old/new journal, journal size, max transaction size, offset, skip journal, keep old parameters, force, standard journal conversion, and super force.

Dependencies and interactions:
- Included by `tune.c`.
- Provides compile-time linkage to optional libuuid support through configure macros.

Risks and notes:
- Several option constants are defined but unused or tied to disabled code paths, reflecting legacy CLI evolution.
