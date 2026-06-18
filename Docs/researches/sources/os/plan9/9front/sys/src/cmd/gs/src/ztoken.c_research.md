# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ztoken.c

## Purpose
Implements token-reading and token-execution operators for files and strings.

## Key Elements
Defines `token`, `.tokenexec`, exported continuation `ztokenexec_continue`, shared continuation logic, comment/DSC comment callout handling, and `ztoken_scanner_options()` for user-parameter driven scanner flags.

## Behavior/Risks
String tokenization uses `scan_string_token` and restores operand-stack depth on scanner errors. File tokenization uses heap-saved `scanner_state` records when refills or callouts suspend scanning. `.tokenexec` differs from `token exec` by leaving literal procedures literal while executable binary object sequences may execute. `%ProcessComment` and `%ProcessDSCComment` are looked up dynamically and called through the exec stack when enabled.

## Dependencies
Integrates with operand, exec, and dictionary stacks; stream/file APIs; scanner state and scanner options; dictionary lookup; and Ghostscript structured allocation.
