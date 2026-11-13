#!/usr/bin/env bash
# One-time setup: Python venv with Manim inside the skill dir, plus a toolchain check.
set -euo pipefail
cd "$(dirname "$0")"
[ -x .venv/bin/python ] || uv venv -q .venv --python 3.12
uv pip install -q --python .venv/bin/python manim requests
for t in ffmpeg ffprobe latex dvisvgm kpsewhich; do
  command -v "$t" >/dev/null || echo "MISSING: $t (Arch: texlive-basic texlive-latex texlive-latexrecommended texlive-fontsrecommended texlive-binextra, ffmpeg)"
done
[ -f .env ] || cp .env.example .env
grep -q '^ELEVENLABS_API_KEY=.\+' .env && echo "key: set in .env" || echo "key: not set, edit $(pwd)/.env"
.venv/bin/python -c "import manim; print('manim', manim.__version__)"
