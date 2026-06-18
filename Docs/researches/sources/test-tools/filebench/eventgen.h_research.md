## sources/test-tools/filebench/eventgen.h

### Purpose
`eventgen.h` exposes the minimal public interface for Filebench's event generator. It lets the main runtime start the generator, configure its rate, and reset the event queue before a benchmark run.

### Important APIs, Types, And Functions
The header declares `eventgen_init(void)`, `eventgen_setrate(avd_t rate)`, and `eventgen_reset(void)`. It includes `filebench.h` to obtain `avd_t` and shared Filebench definitions.

### Control Flow
The header defines no implementation, but the intended sequence is: initialize the eventgen thread, set a rate variable, and reset the queue before worker flowops consume events. Consumers do not include this header directly for queue access; they use shared-memory fields and flowop helpers.

### State And Persistence
State is not declared in the header. The implementation stores all runtime state in `filebench_shm`, so the API remains process-global rather than object-based.

### Dependencies And Integration Points
This is integrated with `eventgen.c`, parser/runtime setup code that calls `eventgen_setrate`, and flowop rate-limit consumers. Its dependency on `filebench.h` ties it to the full Filebench type system rather than a small forward declaration.

### Risks
The API does not expose shutdown or error returns. `eventgen_init` handles errors internally by logging and exiting, so callers cannot recover. The opaque shared-memory state means tests need either Filebench runtime setup or a mock `filebench_shm`.

### Test Signals
Compile tests should verify the header can be included where `filebench.h` is already available. Runtime tests should exercise the implementation sequence and check that rate-setting and reset mutate shared memory as expected.
