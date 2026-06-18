# sources/test-tools/kdevops/scripts/append-makefile-vars.sh

Purpose: concatenates Make/Kconfig variable fragments, with special handling to append only the first eight characters of the second argument as a hash suffix.

Important APIs/types/functions: Bash positional argument handling, substring expansion `${1:0:8}`, and stdout.

Control flow: prints `""` for no args; uses first arg as prefix, second arg truncated to eight chars when present, then appends remaining args verbatim.

State/persistence behavior: stateless stdout helper.

Dependencies/integration: used for generated paths such as hashed SSH config/key names.

Risks/test signals: no quoting around final echo and no separators; callers must supply exact fragments. Test signal is hash truncation matching Terraform tfvars templates.
