# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/test_module.py
# sources/security-integrity/selinux/python/sepolicy/sepolicy/templates/test_module.py

Purpose: template for generating executable policy-module test scripts.

Important APIs and control flow: `dict_values` maps permissions to sample shell actions, while `te_test_module` is a shell/Python-style test template that exercises expected denials/allowances and verifies module behavior. The file is mostly static text, with placeholders for generated paths, labels, and policy rules.

State and persistence: rendered tests create temporary files/directories, run commands, and may rely on installed SELinux policy state. The template itself has no runtime state.

Dependencies and integration points: used by policy generator test output; integrates with shell utilities, SELinux labeling tools, and generated policy modules.

Risks and test signals: generated tests are only as accurate as placeholder data and may require enforcing SELinux plus root privileges. No direct repository test ensures this template stays runnable.
