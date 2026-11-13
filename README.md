# dstack

I'm Dax. I learn the way I debug, which is by finding the exact place where my understanding breaks and fixing that one thing before moving on.

Most of the time an AI tutor gets that backwards. You ask one question and get back a wall of text, so you end up reading more and understanding about the same. The explanation is there but nothing makes you prove you've got it.

**dstack is my answer.** It's a small set of learning skills for coding agents, behind one command called `/lock-in`. You tell it what you're trying to learn, and it works out what's actually in the way. That might be a word you can't pin down, terms that blur together, a subject you can't see the shape of, a mechanism you can't picture, or knowledge you've never been tested on. Then it reaches for the one tool that fixes that problem and leaves the other five alone.

**The agent builds and you think.** The maps, tables, whiteboard pages and videos are scaffolding. The learning happens when you answer questions cold, so every path through dstack leads to the Socratic tutor.

## install

Clone it with its submodules, since two of the skills live in their own repos.

```bash
git clone --recurse-submodules https://github.com/Dakkshin/dstack.git ~/projects/dstack
```

Then point your agent at it.

- If your agent loads a whole folder as a plugin, link the repo in under the name `lock-in`, such as `ln -s ~/projects/dstack ~/.claude/skills/lock-in`. The folder name becomes the root command, and the skills under it come up as `dstack:<name>`.
- If your agent reads plain skill folders from `~/.agents/skills`, link each one in with `for s in ~/projects/dstack/skills/*; do ln -s "$s" ~/.agents/skills/; done`. The skills keep their plain names there.

`manim-explainer` needs a one-time setup for its Python environment and an ElevenLabs key. Run `skills/manim-explainer/setup.sh` and put the key in `skills/manim-explainer/.env`. The other five skills need nothing beyond the clone.

## get started

Type `/lock-in`, then whatever you're learning.

```
/lock-in TCP congestion control, I have an exam on Friday
```

```
/lock-in ~/uni/CSG2305/week3-slides.pdf
```

If you already know which tool you want, put a mode word at the end, which is `define`, `table`, `map`, `sketch`, `video` or `tutor`.

```
/lock-in idempotence define
```

```
/lock-in mutex, semaphore and monitor table
```

## how `/lock-in` decides

It reads the symptom rather than the topic.

| What's going wrong | Where it goes |
|---|---|
| An unfamiliar word is blocking everything else | `define` |
| Two or more terms keep collapsing into each other | `data-table` |
| You don't know where to start, or you've handed it a whole unit | `mindmap` |
| You can recite the steps but couldn't redraw them | `sketch` |
| You think you get it, or the exam is close | `socratic-tutor` |
| You asked for a video, or you want one from a sketch you already have | `manim-explainer` |

When it can't tell, it asks you one question, which is whether the problem is the words, the big picture, how it works, or whether you really know it.

For a whole subject it lays out a path, which is to map the subject, define the terms the map leans on, table anything you keep confusing, sketch the hardest mechanism, and then get tutored to mastery. It runs only the first step and then waits for you, because five artifacts at once is just another wall of text.

Everything for one topic lands in `./<topic>-study/`, along with a `progress.md` that holds the path so far and the tutor's saved state. Come back to the same topic a week later and it picks up from there.

## skills

`/lock-in` runs these for you. You can also call any of them directly.

| Skill | Use it when | What you get |
|---|---|---|
| [`/lock-in`](./SKILL.md) | you want to learn something and aren't sure which tool fits | a diagnosis and the first step, run for you |
| [`define`](./skills/define/SKILL.md) | you need one term pinned down without the textbook around it | a definition of 250 words at most, split into what the term means, what it covers, and one real example |
| [`data-table`](./skills/data-table/SKILL.md) | several terms share a role and you keep swapping them | one table, with columns picked to separate exactly the things you're mixing up |
| [`mindmap`](./skills/mindmap/SKILL.md) | you need the shape of a subject, or want your course files turned into something you can explore | an interactive knowledge tree in one HTML file, built from what the model knows or strictly from your sources |
| [`sketch`](./skills/sketch/SKILL.md) | you can't picture how a mechanism works | a hand-drawn whiteboard page with diagrams that draw themselves step by step and labs where you change the inputs and watch the real computation |
| [`manim-explainer`](./skills/manim-explainer/SKILL.md) | you want to watch an idea unfold, or want something to rewatch before an exam | a narrated 1080p60 video in the style of 3Blue1Brown. It asks which voice you want first, which is Mark, Alex, Will, Matilda or Jessica, and can play you a free sample of each. Rendering costs ElevenLabs credits and a few minutes |
| [`socratic-tutor`](./skills/socratic-tutor/SKILL.md) | you need to prove you actually know it | a session that teaches by asking, tracks each subskill from 0 to 5, re-tests old material without warning, and ends with a final assessment |

<details>
<summary>more examples</summary>

```
/lock-in I keep confusing authentication, authorisation and accounting
/lock-in ~/uni/networks/unit-outline.pdf map
/lock-in how does Diffie-Hellman actually work sketch
/lock-in RSA video
/lock-in quiz me on OSPF, I think I've got it
/lock-in resume from: <a save state block from an earlier tutor session>
```

</details>

## updates

`socratic-tutor` comes from Jane Street's [agent_skills](https://github.com/janestreet/agent_skills) repo. `skills/socratic-tutor` is a link into `vendor/agent_skills`, which is a submodule of that repo. A GitHub Action runs once a day and moves the submodule to Jane Street's latest commit, so `git pull` brings their changes down. You can also run it by hand from the Actions tab.

`sketch` lives in its own repo at [Dakkshin/sketch](https://github.com/Dakkshin/sketch) and is pinned as a submodule. It moves when I bump it here.

## make it yours

Every skill is a single `SKILL.md` and some files beside it, so the fastest way to change how one behaves is to edit its `SKILL.md`. The routing lives in the root [`SKILL.md`](./SKILL.md). If you'd rather the path started with a sketch instead of a map, or wanted the video offered sooner, that's where you change it. How hard the tutor grades lives in its own `SKILL.md`.

## credits

`socratic-tutor` is Jane Street's, under the MIT license that ships in `vendor/agent_skills`.
