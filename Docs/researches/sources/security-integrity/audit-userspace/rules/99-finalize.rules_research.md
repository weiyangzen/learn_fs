# sources/security-integrity/audit-userspace/rules/99-finalize.rules

Purpose: finalization hook to make audit configuration immutable after all rules load.

Important rules: `-e 2` is present but commented out.

Control flow: filename places it at the end so immutability, if enabled, happens after all rule additions.

State and persistence: no effect as shipped; uncommenting sets kernel audit immutable mode until reboot.

Dependencies and integration: parsed by auditctl enabled flag handler.

Risks and test signals: enabling immutable mode prevents later rule changes and can disrupt automation. Test only with reboot access; verify with `auditctl -s`.
