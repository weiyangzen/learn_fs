# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucArgs.cc

## Purpose
Implements `XrdOucArgs`, a getopt-like parser that supports single-character options, optional/required arguments, long option abbreviations, and input from either argv arrays or tokenizer-backed strings.

## Important APIs and control flow
`XrdOucArgsXO` stores one extended option mapping: option word, minimum abbreviation length, one-character mapped value plus option suffix, and linked-list next pointer. Its `%` operator searches for a matching abbreviation and returns the mapped option spec.

The `XrdOucArgs` constructor records error reporting, copies the standard option string, detects leading `:` to change missing-argument return from `?` to `:`, and consumes varargs triples for extended options. `getarg()` returns remaining non-option arguments from the stream or argv. `getopt()` fetches the next token, verifies it begins with `-`, resolves long or single-letter options, handles invalid options, consumes required or optional arguments, rolls back optional arguments that look like options, and reports missing values.

`Set(char*)` attaches a tokenizer to a command string; `Set(int,char**)` switches to argv mode.

## State, dependencies, and integration
State includes tokenizer position, argv index, option specs, current option pointer, `argval`, and error prefix. Dependencies are `XrdOucTokenizer` and `XrdSysError`.

## Risks and test signals
The parser intentionally does not support clustered short options (`-ab`). It uses `strdup/free`, raw varargs, `sprintf` into a fixed buffer for invalid-option messages, and `index()` from strings compatibility headers. Tests should cover required/optional arguments, abbreviation collisions, invalid long options, `:` missing-argument mode, string mode rollback, and reusing one parser via repeated `Set()`.
