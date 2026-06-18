# sources/sync-backup/borg/docs/usage/general/positional-arguments.rst.inc

Purpose: documents Borg's option ordering constraints around positional arguments.

Important APIs and control flow: due to argparse limitations, Borg supports options entirely before or after positional arguments, and some mixed placements, but not options interleaved between archive/path positionals in all cases.

State and persistence: no state; defines command-line parser behavior.

Dependencies and integration points: Python argparse issue 15112, command parser wrappers, and every command with positional arguments.

Risks: users and generated scripts can fail if options are inserted between positionals, especially around archive names and paths. Documentation labels such forms as bad even if adjacent variants work.

Test signals: parser acceptance/rejection tests for options before, after, and between positional arguments across representative commands.
