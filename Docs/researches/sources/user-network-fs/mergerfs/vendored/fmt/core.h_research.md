# sources/user-network-fs/mergerfs/vendored/fmt/core.h

Read signal: read `sources/user-network-fs/mergerfs/vendored/fmt/core.h` completely for this pass (5 lines). Final split target: `Docs/researches/sources/user-network-fs/mergerfs/vendored/fmt/core.h_research.md`.

## Purpose

`core.h` is a compatibility shim in this vendored fmt version. It exists so code including `fmt/core.h` still compiles, but the file comments warn it may be removed in a future version. It recommends `fmt/base.h` for users that do not need `fmt::format` and `fmt/format.h` otherwise.

## Important APIs, Types, and Functions

This file defines no APIs, types, macros, or functions of its own. Its entire operational content is:

- Include `format.h`.

All visible fmt API exposed through this include comes from `format.h`.

## Control Flow

There is no runtime control flow. Preprocessor inclusion of `core.h` immediately includes the vendored `format.h`, so downstream translation units see the same declarations and inline definitions they would receive from `fmt/format.h`.

## State and Persistence Behavior

No state is created or persisted by this file. It relies entirely on the included fmt headers.

## Dependencies and Integration Points

The only direct dependency is the adjacent `format.h`. The integration point is source compatibility for projects that include `fmt/core.h`; in this repository, it keeps mergerfs or third-party vendored code from depending on an upstream fmt layout detail that has changed over time.

## Risks and Edge Cases

- Because this shim includes `format.h`, it may pull in a larger API and implementation surface than newer upstream `fmt/core.h` users expect.
- The comment states the file may be removed in future versions, so local code should prefer the recommended includes when updating fmt.
- Include-order behavior is delegated to `format.h`; this file does not have its own include guard, so protection depends on `format.h` guards and normal compiler include handling.

## Test Signals

The useful test is build coverage: translation units that include `fmt/core.h` should compile and link exactly as if they included `fmt/format.h`. Any vendored fmt upgrade should include an include-compatibility check for `fmt/core.h`.
