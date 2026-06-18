# sources/storage-engines/foundationdb/fdbrpc/ActorFuzz.actor.cpp

Purpose: generated actor-compiler fuzz corpus. It defines many small actors with varied control-flow constructs and an `actorFuzzTests` harness that asserts generated actors emit expected traces and return/error sentinels.

Important APIs and functions: generated `ACTOR Future<int> actorFuzz0` through `actorFuzz29` take `FutureStream<int> inputStream`, `PromiseStream<int> outputStream`, and `Future<Void> error`. `actorFuzzTests()` calls `testFuzzActor` for each actor and returns `{testsOK, 30}`.

Control flow: actors combine `state` variables, nested loops, range loops, `try/catch`, `continue`, `break`, `return`, `waitNext(inputStream)`, `wait(error)`, `throw operation_failed`, and `throw_operation_failed`. They send numeric markers to `outputStream`; expected vectors encode the correct actor lowering behavior.

State and persistence behavior: no persistent state. Each actor maintains actor-local state-machine variables generated for Flow's actor compiler.

Dependencies and integration points: includes `fdbrpc/ActorFuzz.h` and `flow/actorcompiler.h` last, as required by actor source transformation. Linked into tests through `ActorFuzzUnitTest.cpp`.

Risks: the file is generated and should not be edited directly. Expected marker sequences are brittle by design; generator changes require regenerating both actor bodies and expected outputs. It is excluded on Windows via `#ifndef WIN32`.

Test signals: very high signal for actor compiler semantics across exception and control-flow cases; low signal for application behavior because this is compiler/runtime validation.
