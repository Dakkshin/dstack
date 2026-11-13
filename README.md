# dstack

These are the skills I use when I'm studying with AI. I wrote them for my own uni units, mostly because asking a chatbot to explain something gave me long answers that didn't stick.

`/lock-in` is the one command you need. You give it a topic or your course files, and it picks one of six tools based on what you're stuck on. That might be a short definition, a comparison table, a mindmap of the whole subject, a whiteboard-style explainer, a narrated video, or a tutor that quizzes you until you actually know it. It does one step at a time, and once there's something to test you on it steers you to the tutor.

## install

Clone it with its submodules, because two of the skills live in their own repos.

```bash
git clone --recurse-submodules https://github.com/Dakkshin/dstack.git ~/projects/dstack
```

Then point your AI app at it. A skill is a folder of plain instructions that an app can load, so dstack works in any app that reads skills.

- If your app loads a whole folder as a plugin, link the repo into its skills folder under the name `lock-in`, as in `ln -s ~/projects/dstack <skills folder>/lock-in`. The folder name becomes the command, which is why it's `/lock-in`, and the skills under it show up as `dstack:<name>`.
- If your app reads plain skill folders from `~/.agents/skills`, link each one in with `for s in ~/projects/dstack/skills/*; do ln -s "$s" ~/.agents/skills/; done`. The skills keep their plain names there.

`manim-explainer` needs a one-time setup, which is its Python environment and an ElevenLabs key for the voice. Run `skills/manim-explainer/setup.sh` and then put the key in `skills/manim-explainer/.env`. The other five skills work straight after the clone.

## get started

Type `/lock-in` and then whatever you're learning.

```
/lock-in photosynthesis, I have a biology exam on Friday
```

```
/lock-in ~/uni/week3-slides.pdf
```

If you already know which tool you want, put a mode word at the end. The mode words are `define`, `table`, `map`, `sketch`, `video` and `tutor`.

```
/lock-in opportunity cost define
```

```
/lock-in mitosis, meiosis and binary fission table
```

## how `/lock-in` decides

It looks at what's going wrong for you rather than at the topic.

| What's going wrong | Where it goes |
|---|---|
| A word you don't know is blocking everything else | `define` |
| Two or more terms keep blurring into each other | `data-table` |
| You don't know where to start, or you've handed it a whole unit | `mindmap` |
| You can recite the steps but couldn't draw them | `sketch` |
| You think you get it, or the exam is close | `socratic-tutor` |
| You asked for a video, or you want one made from a sketch you already have | `manim-explainer` |

When it can't tell, it asks you one question, which is whether the problem is the words, the big picture, how it works, or whether you really know it.

For a whole subject it lays out a path. It maps the subject first and then defines the terms the map leans on. After that it tables anything you keep mixing up, sketches the hardest part, and tutors you until you know it. It only runs the first step and then waits for you to pick the next one.

Everything for one topic goes into a `./<topic>-study/` folder, along with a `progress.md` file that keeps the path so far and where the tutor left off. If you come back to the same topic a week later, it picks up from there.

## skills

`/lock-in` runs these for you, but you can also call any of them on its own.

| Skill | Use it when | What you get |
|---|---|---|
| [`/lock-in`](./SKILL.md) | you want to learn something and aren't sure which tool fits | it works out what you're stuck on and runs the first step for you |
| [`define`](./skills/define/SKILL.md) | you need one term pinned down without a textbook's worth of context around it | a definition of 250 words at most, which covers what the term means, what falls under it, and one real example |
| [`data-table`](./skills/data-table/SKILL.md) | a few terms do similar jobs and you keep swapping them | one table, in which the columns are picked to separate the things you're mixing up |
| [`mindmap`](./skills/mindmap/SKILL.md) | you need the shape of a whole subject, or want your course files turned into something you can explore | an interactive map of the subject in one HTML file. It's built from what the model knows, or only from your own files if you give it some |
| [`sketch`](./skills/sketch/SKILL.md) | you can't picture how something works | a hand-drawn whiteboard page, in which the diagrams draw themselves step by step and the labs let you change the inputs and watch what happens |
| [`manim-explainer`](./skills/manim-explainer/SKILL.md) | you want to watch an idea unfold, or want something to rewatch before an exam | a narrated video in the style of 3Blue1Brown. It asks which voice you want first, which is Mark, Alex, Will, Matilda or Jessica, and it can play you a free sample of each. Making the video costs ElevenLabs credits and takes a few minutes |
| [`socratic-tutor`](./skills/socratic-tutor/SKILL.md) | you need to prove you actually know it | a session that teaches by asking you questions. It scores each part of the topic from 0 to 5, re-tests old material without warning, and ends with a final test |

<details>
<summary>more examples</summary>

```
/lock-in I keep mixing up weather and climate
/lock-in ~/uni/psychology/unit-outline.pdf map
/lock-in how does a vaccine train the immune system sketch
/lock-in compound interest video
/lock-in quiz me on the French Revolution, I think I've got it
/lock-in resume from: <the saved block from an earlier tutor session>
```

</details>

## updates

`socratic-tutor` comes from Jane Street's [agent_skills](https://github.com/janestreet/agent_skills) repo. In this repo `skills/socratic-tutor` is a link into `vendor/agent_skills`, which is a submodule, meaning git's way of keeping another repo inside this one at a fixed version. A GitHub Action runs once a day and moves it to Jane Street's latest version, so a `git pull` here brings their changes down. You can also run the Action by hand from the Actions tab.

`sketch` lives in its own repo at [Dakkshin/sketch](https://github.com/Dakkshin/sketch) and is also kept here as a submodule. It only moves when I update it.

## make it yours

Each skill is one `SKILL.md` file plus a few files beside it, so the quickest way to change how a skill behaves is to edit its `SKILL.md`. The routing lives in the root [`SKILL.md`](./SKILL.md). That's the file to edit if you'd rather the path started with a sketch instead of a map, or you want the video offered sooner. How strictly the tutor grades you is set in its own `SKILL.md`.

## credits

`socratic-tutor` is Jane Street's, and it's under the MIT license that ships in `vendor/agent_skills`.
