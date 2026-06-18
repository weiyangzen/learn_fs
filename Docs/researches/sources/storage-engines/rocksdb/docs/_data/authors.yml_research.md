## sources/storage-engines/rocksdb/docs/_data/authors.yml

### Purpose

`docs/_data/authors.yml` stores Jekyll data records for blog/documentation authors keyed by standardized GitHub-style user names. Each record provides at least `full_name`, and some include a legacy Facebook ID under `fbid`.

### Important APIs, Types, And Functions

This is YAML data consumed as `site.data.authors` by Liquid templates. Keys include `icanadi`, `xjin`, `leijin`, `yhciang`, `radheshyam`, `zagfox`, `lgalanis`, `siying`, `dmitrism`, `rven2`, `yiwu`, `maysamyabandeh`, `IslamAbdelRahman`, `ajkr`, `abhimadan`, `sagar0`, `lightmark`, `fgwu`, `ltamasi`, `cbi42`, `zjay`, `hx235`, `pdillinger`, `alanpaxton`, `akankshamahajan15`, `anand1976`, `poojam23`, and `joshkang97`.

### Control Flow

Jekyll loads the file into the data namespace at build time. Layouts or includes can resolve a post author's ID to a display name and optional profile image source. The comments state that IDs should be standardized on GitHub user names and that `fbid` is optional and legacy.

### State And Persistence Behavior

The file is static site metadata. Changes affect generated author bylines and possibly profile image lookup; no runtime state is mutated.

### Dependencies And Integration Points

It integrates with posts/front matter that reference these author IDs and with layouts/includes that read `site.data.authors`. It overlaps with author entries embedded in `_config.yml`, so templates may have two possible sources.

### Risks And Edge Cases

- Author IDs are case-sensitive in YAML/Liquid; `IslamAbdelRahman` uses mixed case while most IDs are lowercase.
- Missing `fbid` must be tolerated by templates because several records omit it.
- Duplication with `_config.yml` risks drift if an author's name changes in only one location.
- Since Facebook IDs are legacy, privacy or broken-image behavior should be considered if templates still fetch remote profile images.

### Test Signals

Build pages with authors that have and lack `fbid`, verify bylines resolve correctly, and check that unknown author IDs fail gracefully. Static research only; no Jekyll command was run.
