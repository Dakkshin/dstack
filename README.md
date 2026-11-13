# dstack

dstack is a learning kit for Claude Code. You tell it what you're trying to learn, and it works out what's actually in the way, which might be a word you can't pin down, terms that blur together, a subject you can't see the shape of, a mechanism you can't picture, or knowledge you haven't tested yet. Then it reaches for the one tool that fixes that.

Type `/dstack <topic or path to course files>`, optionally followed by a mode word, which is `define`, `table`, `map`, `sketch`, `video` or `tutor`.

| Skill | What it's for |
|---|---|
| `dstack` (root) | Diagnoses the sticking point and routes to one of the skills below |
| `dstack:define` | A bounded definition of 250 words at most |
| `dstack:data-table` | A table that separates terms you keep mixing up |
| `dstack:mindmap` | An interactive knowledge tree of a whole subject or a set of course files |
| `dstack:sketch` | A hand-drawn whiteboard explainer with step-through diagrams and live labs |
| `dstack:manim-explainer` | A narrated 3Blue1Brown-style video, which needs an ElevenLabs key in its `.env` |
| `dstack:socratic-tutor` | A question-led session that drills you to mastery and tracks a skill map |

## Layout

The plugin lives at `~/projects/dstack`, and `~/.claude/skills/dstack` is a symlink to it, so Claude Code loads it in place as `dstack@skills-dir`. The six skill folders are real folders under `skills/`, and `~/.agents/skills/<name>` symlinks back to each one so that pi, opencode and Antigravity keep reading the same files. `skills/sketch` is also its own git repo (github.com/Dakkshin/sketch).

Disable it with `claude plugin disable dstack@skills-dir`.
