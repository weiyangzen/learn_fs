## sources/test-tools/filebench/fbtime.h

### Purpose
`fbtime.h` abstracts high-resolution time definitions for Filebench. It declares a fallback `hrtime_t` and `gethrtime` only on systems that lack a native implementation, and it defines floating conversion constants.

### Important APIs, Types, And Functions
When `HAVE_GETHRTIME` is absent, the header typedefs `hrtime_t` to `uint64_t` and declares `gethrtime(void)`. It defines `SEC2NS_FLOAT` and `SEC2MS_FLOAT` as floating constants for seconds-to-nanoseconds and seconds-to-micro/millisecond-style scaling used by timing calculations.

### Control Flow
There is no runtime control flow. Compile-time configuration controls whether the fallback type and function declaration are visible.

### State And Persistence
The header defines no state. It standardizes units and declarations for code that needs elapsed time.

### Dependencies And Integration Points
It includes `config.h` and conditionally `stdint.h`. `fbtime.c` implements the fallback. Filebench modules use the constants and `gethrtime` name without caring whether the platform is Solaris-like or using the fallback.

### Risks
Callers may assume monotonic nanosecond precision even on fallback builds where `fbtime.c` uses `gettimeofday`. The macro `SEC2MS_FLOAT` is named as milliseconds but set to `1000000.0`, which is microseconds per second; callers need to understand the intended unit context.

### Test Signals
Build tests should cover both native and fallback configurations. Runtime tests should validate elapsed-time arithmetic in event generation and reports on fallback systems.
