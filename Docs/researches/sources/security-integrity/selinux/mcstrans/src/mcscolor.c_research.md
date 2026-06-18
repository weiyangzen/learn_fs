<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcscolor.c -->
# sources/security-integrity/selinux/mcstrans/src/mcscolor.c

## Purpose

Color translation engine for SELinux contexts. It parses `secolor.conf`, maps raw MLS/MCS patterns to foreground/background color strings, supports color mnemonics, and selects the best matching pattern for a raw context. The source was read completely for this report (362 lines).

## Important APIs, Types, and Functions

Exports `init_colors()`, `finish_context_colors()`, and `raw_color()`. Internal helpers include `check_dominance()` for pattern matching, `add_secolor()`, `find_mnemonic()`, `add_mnemonic()`, `process_color()`, and `parse_components()`.

## Control Flow

Initialization reads `selinux_colors_path()`, processes mnemonic and context color lines, and stores mappings in memory. `raw_color()` parses a context, compares raw range/category dominance against configured patterns, and returns a string color pair.

## State and Persistence Behavior

State is static color/mnemonic arrays or lists populated at init and freed by finish. No persistent writes occur.

## Dependencies and Integration Points

Depends on libselinux context/path APIs, local MLS parsing utilities, stdio parsing, and config files such as `secolor.conf` examples.

## Risks and Edge Cases

Risks include parser ambiguity, malformed hex colors, dominance matching errors for category ranges, and stale state if reload cleanup does not precede reinit.

## Test Signals

Test signals are `mlscolor-test`, example `secolor.conf` cases, daemon raw-color requests, and malformed color-line tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcscolor.c -->
