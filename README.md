# dstack

dstack is a learning kit for Claude Code, and `/lock-in` is its front door. You tell it what you're trying to learn, and it works out what's actually in the way, which might be a word you can't pin down, terms that blur together, a subject you can't see the shape of, a mechanism you can't picture, or knowledge you haven't tested yet. Then it reaches for the one tool that fixes that.

Type `/lock-in <topic or path to course files>`, optionally followed by a mode word, which is `define`, `table`, `map`, `sketch`, `video` or `tutor`.

| Skill | What it's for |
|---|---|
| `/lock-in` (root) | Diagnoses the sticking point and routes to one of the skills below |
| `dstack:define` | A bounded definition of 250 words at most |
| `dstack:data-table` | A table that separates terms you keep mixing up |
| `dstack:mindmap` | An interactive knowledge tree of a whole subject or a set of course files |
| `dstack:sketch` | A hand-drawn whiteboard explainer with step-through diagrams and live labs |
| `dstack:manim-explainer` | A narrated 3Blue1Brown-style video, which needs an ElevenLabs key in its `.env` |
| `dstack:socratic-tutor` | A question-led session that drills you to mastery and tracks a skill map |

## Layout

The plugin lives at `~/projects/dstack`, and `~/.claude/skills/lock-in` is a symlink to it, so Claude Code loads it in place as `dstack@skills-dir`. The root command takes its name from that symlink, which is why it is `/lock-in` while the skills under it are `dstack:<name>`. The six skill folders are real folders under `skills/`, and `~/.agents/skills/<name>` symlinks back to each one so that pi, opencode and Antigravity keep reading the same files. `skills/sketch` is a submodule of github.com/Dakkshin/sketch. `skills/socratic-tutor` is a link into `vendor/agent_skills`, which is a submodule of Jane Street's github.com/janestreet/agent_skills. A daily GitHub Action (`.github/workflows/update-socratic-tutor.yml`) moves that submodule to Jane Street's latest commit and pushes the bump, so `git pull` here brings the update down.

Clone with `git clone --recurse-submodules`, since the two submodules are empty otherwise.

Disable it with `claude plugin disable dstack@skills-dir`.
