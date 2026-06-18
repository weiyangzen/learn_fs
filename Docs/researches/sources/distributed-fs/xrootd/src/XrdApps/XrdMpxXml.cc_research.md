# sources/distributed-fs/xrootd/src/XrdApps/XrdMpxXml.cc

Purpose: converts XRootD `<statistics>` XML streams into compact CGI, flat key/value, or human text output for `mpxstats` and `xrdqstats`.

Important APIs/types/functions: file-local `vnMap` maps dotted XML variable names to text labels and marks time fields with `~`; `XrdMpxVar` maintains a dotted element stack with `Push`, `Pop`, `Reset`, and `Var`; `XrdMpxXml::Format` performs parsing and formatting; `Add` emits one variable/value pair; `getVars` parses XML-style attributes from the tokenizer; `xmlErr` reports malformed streams.

Control flow: `Format` first rewrites the input buffer in place to make tokens line-oriented, validates that the first record starts with `<statistics`, extracts header attributes (`tod`, `ver`, `src`, `tos`, `pgm`, `ins`, `pid`), appends an optional host, then walks tokens until `/statistics`. Opening tags push stack names, `stats id="..."` pushes the id value, closing tags pop, and text tokens are emitted under the current dotted path. Tail attribute `toe` is appended when present.

State and persistence: conversion state is transient. `Format` mutates its input buffer by replacing delimiters with whitespace/newlines and trimming quotes, so callers must not expect the original XML to remain intact. No persistent storage is used.

Dependencies and integration points: uses `XrdOucTokenizer`; called by XrdApps utilities that query or receive stats. The text-label map hardcodes XRootD statistic schema knowledge.

Risks: parsing is token-based rather than XML-compliant, so unusual whitespace, escaping, nested text, or larger messages can misparse. Output uses unbounded `strcpy` into caller-provided buffers. `XrdMpxVar::Push` can partially modify `vEnd` before detecting some fence failures. Text time conversion uses `localtime`, which is not thread-safe.

Test signals: compare XML-to-flat/CGI/text conversion for representative stats payloads, malformed XML, deep nesting, zero suppression, quoted values, time fields, and unknown variable names.
