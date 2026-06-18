## sources/test-tools/syzkaller/sys/generated/generated.go

Purpose: provides compressed gob serialization/deserialization and registration of generated syscall descriptions into `prog.Target`.

Important APIs/types/functions: `Desc`, `Register`, `fill`, `Serialize`, `FileName`, `Glob`, `fileName`, and `init` gob registrations.

Control flow: generated OS/arch packages call `Register`, which builds a target from `targets.List` metadata and registers filler/init callbacks. `fill` reads `gen/<os>_<arch>.gob.flate`, decompresses and gob-decodes a `Desc`, and populates target syscalls/resources/constants/flags/types. `Serialize` performs the inverse for generation tooling.

State and persistence: reads embedded generated gob files; writes serialized bytes only to caller-provided destinations. Registers concrete `prog.Type` and expression implementations with gob at init time.

Dependencies/integration: central bridge between compiler-generated descriptions and runtime target registration.

Risks: missing embedded files panic at target init. Gob registration must include every concrete type stored in `Desc`. File naming must stay stable for generators and embed patterns.

Test signals: indirectly exercised by every `GetTarget` and all-target test.
