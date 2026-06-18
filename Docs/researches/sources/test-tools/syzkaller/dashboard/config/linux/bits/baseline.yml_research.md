# sources/test-tools/syzkaller/dashboard/config/linux/bits/baseline.yml

Purpose: trims baseline Linux configs below defconfig by disabling subsystems that are not needed for baseline fuzzing.

Important keys: disables DRM, integrity/EVM/IMA families with weak tags, joystick/LED/mouse/tablet/touchscreen, KCOV with weak tags, Macintosh/PS2 mouse, NetLabel, PCCARD, `PREEMPT_VOLUNTARY` except ARM, RFKILL, sound, TPM, wireless, and related wireless extension symbols.

Control flow: declarative list applied to baseline-tagged generated configs.

State and persistence: modifies generated `.config` only.

Dependencies and integration points: baseline manager profiles, Kconfig weak override semantics, and architecture tags.

Risks: weak disables depend on generator semantics; if dependencies re-enable symbols strongly, baseline size/noise may grow. Disabling KCOV in baseline changes coverage expectations compared with full fuzzing configs. Excluding ARM from `PREEMPT_VOLUNTARY` reflects arch defaults and must be revisited if defaults change.

Test signals: baseline kernels should be smaller/faster while still booting and supporting intended baseline tasks.
