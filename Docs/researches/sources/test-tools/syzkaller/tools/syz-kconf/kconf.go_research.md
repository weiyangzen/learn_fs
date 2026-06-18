# sources/test-tools/syzkaller/tools/syz-kconf/kconf.go

Purpose: `syz-kconf` generates Linux kernel config files for dashboard instances from YAML config fragments and a kernel source tree.

Important APIs and flow: `main` opens a Linux repo, parses the main spec, checks config feature constraints, groups instances by kernel revision, checks out each revision, determines release tag, and generates matching instances in parallel. `Context.generate` creates a temp build dir, selects target arch from features, parses Kconfig, derives release features, runs `mrproper` when needed, executes configured shell commands, parses `.config`, adds dependent USB/HID distro configs unless baseline, applies requested configs, converts modules to yes unless module mode, explicitly disables missing bool/tristate configs, writes `.config` and a `.tmp` debug copy, runs `olddefconfig`, verifies final config, converts modules to no if needed, and writes the generated config header plus serialized config and verbatim content. Supporting methods run shell/make commands, apply choice configs, verify optional/selected configs, add dependent configs from distro fragments, set release feature flags, and replace variables.

State and persistence: checks out and may clean the kernel source repo, creates temp build dirs, writes generated `<instance>.config` and `<instance>.config.tmp` files beside the spec, and reads many YAML fragments and Kconfig files.

Dependencies and integration: uses `pkg/vcs`, `pkg/kconfig`, Linux build helpers, target metadata, YAML parser via `parser.go`, and external `make`.

Risks: kernel checkout/build side effects, long-running make commands, parallel generation sharing one source dir per revision, feature mistakes causing incorrect configs, and `.tmp` debug files intentionally left on verification failure. `checkConfigs` warns on `CONFIG_` prefixes but returns all accumulated problems as an error.

Test signals: `kconf_test.go` covers release tag parsing and YAML node parsing. Full generation requires integration tests with a kernel tree.
