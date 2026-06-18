# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucArgs.hh

## Purpose
Declares the `XrdOucArgs` command-line parser used by XRootD utilities and interactive command code.

## Important APIs and types
`getopt()` returns option identifiers similarly to C `getopt()`, with `?`, `:`, or `-1` signaling invalid option, missing value, or option-list exhaustion. `getarg()` returns positional arguments after option parsing. `Set(char*)` and `Set(int,char**)` choose string-tokenizer or argv input. The constructor accepts a standard option specification plus varargs triples for extended options: long word, minimum abbreviation length, and mapped one-character option spec.

The public `argval` points to the current option argument when one is consumed.

## State, dependencies, and integration
The class embeds `XrdOucTokenizer`, stores error target/prefix, linked extended options, valid option string, current option cursor, argv position, and missing-argument return policy. It forward-declares `XrdSysError` and `XrdOucArgsXO`.

## Risks and test signals
The varargs constructor is type-unsafe and must be terminated with a null option word. Consumers must not assume POSIX clustered short-option behavior. Tests should include documented examples such as `debug` and `force`, optional argument behavior with following `-` tokens, and parser reuse.
