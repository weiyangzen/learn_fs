# sources/storage-engines/wiredtiger/tools/wt-config-format

Purpose: formats WiredTiger configuration strings or Turtle files into a more readable indented form.

Important APIs and control flow: a Bash wrapper invokes a single Perl `-npE` expression. For lines containing `=` and an opening delimiter, it rewrites commas and parentheses/braces/brackets into newlines with indentation based on nesting depth.

State and persistence behavior: reads stdin or file arguments and writes formatted text to stdout. It does not modify inputs.

Dependencies and integration points: depends on Bash and Perl. Used manually for inspecting WT config strings, including `WiredTiger.turtle` content.

Risks: this is a lexical formatter, not a full WT config parser; quoted delimiters or unusual syntax can be reformatted incorrectly. Indentation counter is per input line because `$i=0` is reset for each line.

Test signals: piping a nested config string should produce line breaks after commas and nested indentation; no automated test is present.
