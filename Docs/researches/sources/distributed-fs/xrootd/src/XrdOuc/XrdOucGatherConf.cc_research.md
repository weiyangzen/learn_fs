# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGatherConf.cc

## Purpose
Implements a configuration-gathering helper that extracts selected directives or directive prefixes into a tokenizable buffer for later plugin/config parsing.

## Important APIs, Types, And Functions
Private `XrdOucGatherConfData` stores an `XrdOucTokenizer`, optional `XrdSysError`, last line, wanted-match list, gathered buffer, and echo ordering. Constructors build an `XrdOucTList` of exact or prefix matches. Implemented public methods include `EchoLine`, `EchoOrder`, `Gather`, `GetLine`, `GetToken`, `hasData`, `LastLine`, message helpers, `RetToken`, `Tabs`, and `useData`.

## Control Flow
`Gather` opens a config file, attaches `XrdOucStream` with a fresh `XrdOucEnv`, scans first words after substitutions/conditionals, matches exact directives or prefixes ending in `.`, optionally trims the prefix, copies rest-of-line into `body`, appends selected lines or bodies to `theGrab`, then duplicates the result into `gBuff` and attaches the tokenizer. `GetLine` skips empty lines and records `lline`. Message helpers require an error object and print the last line before or after the diagnostic based on `EchoOrder`.

## State And Persistence
State is in-memory selected config text and tokenizer position. Persistent input is the config file; no output file is written. Existing gathered data is freed before new gather/useData.

## Dependencies And Integration Points
Depends on `XrdOucEnv`, `XrdOucStream`, `XrdOucString`, `XrdOucTList`, `XrdOucTokenizer`, `XrdSysError`, POSIX `open`, and errno. It integrates with plugins that need only their directive subset from a full xrootd config.

## Risks And Test Signals
Risks include a constructor overload bug where the `const char**` loop never increments `i`, fixed 64-byte directive and 4096-byte body buffers, message methods throwing when no error object exists, and subtle `trim_body`/`only_body` differences. Test signals include prefix and exact matching, all four gather levels, initial `parms` prepending, oversized directive/body errors, tokenizer backup, echo ordering, and vector constructor coverage.
