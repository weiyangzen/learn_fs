# sources/storage-engines/foundationdb/contrib/gen_compile_db.py

## Purpose
Transforms `compile_commands.json` for better editor/indexer support, especially mapping generated Flow actor files back to source actor files and adding Swift compile commands from Ninja.

## Important APIs, Types, And Functions
`actorFile()` rewrites build paths and `actor.g.cpp`/`actor.g.h` to source `actor.cpp`/`actor.h`. `rreplace()` replaces the last occurrence of a substring. `actorCommand()` rewrites compile command source path for generated actor C++ commands. Optional `-ninjatool` invokes `ninja -t compdb` to collect Swift commands.

## Control Flow
The script loads an input compile database, optionally builds a map of Swift compile commands from Ninja while filtering header-emission commands, then iterates original commands. It replaces `-DNO_INTELLISENSE` with `-Wno-unknown-attributes`, rewrites generated actor entries to source files, substitutes Swift entries from Ninja when available, and writes the processed JSON.

## State And Persistence
Reads one compile database and writes `processed_compile_commands.json` by default. No other persistent state.

## Dependencies And Integration
Uses Python stdlib JSON, regex, subprocess, and shlex. Integrates with Flow actor generated files and Swift build commands in FoundationDB.

## Risks
Regex `-c (.+)(actor\.g\.cpp)` is greedy and command-string based, so quoted paths or unusual flags can be mishandled. Broad `except:` around Ninja acquisition hides failures. `actorFile()` uses simple string replacement and can rewrite unintended path prefixes. The `-s` help text incorrectly says build directory.

## Test Signals
Synthetic compile database entries for normal C++, actor generated files, actor headers, Swift files with and without Ninja commands, quoted paths, and failed Ninja invocation.
