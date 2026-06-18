# sources/security-integrity/libcap/pam_cap/test.c

Purpose: minimal smoke test for the PAM module authentication entry point.

Important APIs/functions: includes PAM headers and calls `pam_sm_authenticate(NULL, 0, 0, NULL)`, expecting `PAM_SUCCESS`.

Control flow: if the module call does not return success, it prints a failure and exits 1; otherwise exits 0.

State and dependencies: no persistent state. It links against the PAM module entry point and relies on the module's no-argument behavior in the build/test context.

Risks and test signals: because it uses a null PAM handle and no module arguments, it is only a narrow ABI/smoke signal. More complete behavior is covered by `test_pam_cap.c`.
