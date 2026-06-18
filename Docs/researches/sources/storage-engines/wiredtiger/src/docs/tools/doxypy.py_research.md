# sources/storage-engines/wiredtiger/src/docs/tools/doxypy.py

## Purpose
Vendored `doxypy` input filter that converts Python docstrings into Doxygen-compatible comment blocks before documentation generation.

## Important APIs and control flow
`FSM` implements transition-driven parsing. `Doxypy` configures regexes for single and double triple-quoted strings, `def`/`class` lines, multiline definitions, imports, comments, and empty lines. The FSM tracks file head, definition/class discovery, body, multiline definition, and docstring states. Callback methods collect docstrings, optionally prefix a brief line, emit `##` plus `#` comment lines at the same indentation, and then emit the triggering definition/class block. `parseFile` streams input line by line and flushes output. `optParse` supports `--autobrief` and `--debug`.

## State, dependencies, integration, risks
Parser state lives in `output`, `comment`, `filehead`, `defclass`, `indent`, and FSM current state. It depends on Python `re`, `sys`, and `optparse`. It integrates with `pyfilter`, which pipes its output into `fixlinks.py`, and with Doxygen filter settings. Risks include Python 2-era idioms, mutable default argument in `FSM.__init__`, limited syntax recognition for decorators/async/type annotations, docstring association edge cases, and GPL licensing considerations for vendored tooling. Test signals are module, class, function, multiline definition, raw/unicode docstring, autobrief, no-docstring, and broken-pipe cases.
