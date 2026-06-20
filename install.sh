#!/usr/bin/env bash
set -euo pipefail

# ============================================================
#  Установка персонального астролога для Claude Code
#
#  ПЕРЕД ОТПРАВКОЙ КСЕНИИ (делает Далер, один раз):
#    1. Впиши в REPO_URL ссылку с токеном (инструкция в README.md).
#    2. Переименуй файл:  mv install.sh install.command
#    3. Сделай исполняемым: chmod +x install.command
#    4. Отправь ей install.command (Telegram/почта).
# ============================================================

REPO_URL="${ASTRO_REPO_URL:-https://<ТОКЕН>@github.com/rakhmondaler/fates-of-xenia.git}"
SKILL_NAME="fates"
DEST="${ASTRO_DEST:-$HOME/.claude/skills/$SKILL_NAME}"

echo ""
echo "✨  Ставлю твоего личного астролога для Claude Code…"
echo ""

# 1. Проверки окружения
if ! command -v git >/dev/null 2>&1; then
  echo "❌  Не найден git. Установи инструменты разработчика командой:"
  echo "    xcode-select --install"
  echo "    Потом запусти этот файл ещё раз."
  exit 1
fi
if ! command -v claude >/dev/null 2>&1; then
  echo "⚠️   Claude Code не найден в системе. Файлы поставлю, но пользоваться"
  echo "    скиллом нужно внутри Claude Code."
fi

# 2. Скачивание во временную папку
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
echo "📥  Скачиваю данные…"
if ! git clone --depth 1 "$REPO_URL" "$TMP/repo" >/dev/null 2>&1; then
  echo "❌  Не удалось скачать. Проверь интернет или попроси Далера прислать"
  echo "    файл заново (мог устареть доступ)."
  exit 1
fi

# 3. Раскладка в папку скиллов Claude Code
echo "📂  Раскладываю файлы…"
mkdir -p "$DEST"
# чистим старое (кроме .venv), чтобы обновление было чистым
find "$DEST" -mindepth 1 -maxdepth 1 ! -name '.venv' -exec rm -rf {} + 2>/dev/null || true
cp "$TMP/repo/SKILL.md" "$DEST/"
cp -R "$TMP/repo/data" "$DEST/"
cp -R "$TMP/repo/scripts" "$DEST/"

# 4. Эфемериды для точных транзитов (если не встанет — скилл берёт из веба)
echo "🔭  Настраиваю точный расчёт транзитов…"
if command -v python3 >/dev/null 2>&1; then
  if python3 -m venv "$DEST/.venv" >/dev/null 2>&1 \
     && "$DEST/.venv/bin/pip" install -q --upgrade pip >/dev/null 2>&1 \
     && "$DEST/.venv/bin/pip" install -q pyswisseph >/dev/null 2>&1; then
    echo "    ✓ Точные транзиты включены."
  else
    echo "    ⚠️ Не вышло — транзиты будут считаться через интернет (это тоже ок)."
  fi
else
  echo "    ⚠️ Нет python3 — транзиты будут считаться через интернет (это тоже ок)."
fi

echo ""
echo "✅  Готово! Астролог установлен."
echo ""
echo "Как пользоваться:"
echo "  1. Открой Claude Code."
echo "  2. Просто напиши, например:"
echo "       «что у меня по транзитам сегодня?»"
echo "       «расскажи про мой характер по карте»"
echo "       «помоги понять, что со мной происходит»"
echo ""
