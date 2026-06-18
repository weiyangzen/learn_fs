# Research: sources/test-tools/syzkaller/pkg/report/netbsd.go

Purpose: configures the shared BSD reporter for NetBSD crash logs. It defines NetBSD-specific oops patterns and stack symbolization regexps while reusing `bsd` parsing/symbolization mechanics.

Important APIs/types/functions: `ctorNetbsd` creates stack and witness symbolization regexps, appends a postfix `event_init` ignore, and calls `ctorBSD`. `netbsdOopses` handles supervisor faults, kernel diagnostic assertions, lock errors, ASan unauthorized access, MSan uninitialized memory, UBSan undefined behavior, group Go runtime errors, and common syzkaller failures.

Control flow: construction injects NetBSD-specific patterns into a generic `bsd` instance. Runtime `ContainsCrash`, `Parse`, and `Symbolize` are inherited from `bsd`: line matching uses `netbsdOopses`, title extraction is `simpleLineParser`, and matching stack lines can be decorated with file:line data from the NetBSD kernel object.

State and persistence: no NetBSD-specific mutable state. Symbol tables and kernel object paths are held by `bsd` if kernel object configuration is supplied.

Dependencies and integration points: selected by `ctors[targets.NetBSD]`; depends on `ctorBSD`, shared `oops` formatting, common syzkaller oopses, and `stackParams`-independent title extraction. Fixtures under `testdata/netbsd` and shared `all` fixtures run through this backend.

Risks: NetBSD panic formats are encoded as multiline regexps; minor wording changes can cause fallback titles or missed reports. The added `event_init` ignore suppresses known postfix output but could hide a real crash if the same text appears in a meaningful context. Symbolization regexps assume `netbsd:function+offset` and witness `#N function+offset` shapes.

Test signals: `netbsd_test.go` validates normal, inline, missing-symbol, and witness symbolization forms. Parse fixtures should cover each sanitizer/panic oops format.
