# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/boolean.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/boolean.py

Purpose: data-only template module for generated SELinux tunables/booleans.

Important APIs and control flow: exposes `te_boolean`, a template that emits a documented `gen_tunable(BOOLEAN, false)`, and `te_rules`, a `tunable_policy('BOOLEAN', '#TRUE', '#FALSE')` wrapper. There is no executable control flow; callers substitute `BOOLEAN`, `#TRUE`, and `#FALSE`.

State and persistence: no runtime state. Persistence occurs when the policy generator writes the rendered template into generated `.te` files.

Dependencies and integration points: consumed by `sepolicy generate` style tooling that assembles templates into policy modules.

Risks and test signals: generated policy defaults booleans to false, which is conservative but can surprise generated-module users if template consumers do not replace placeholder text. No direct unit tests cover rendered boolean syntax.
