#!/usr/bin/env bash
# qsim — one-shot installer for Debian 12 and CachyOS/Arch
#
# Użycie:
#   curl -fsSL https://raw.githubusercontent.com/SyriusM/qsim/main/install.sh | bash
# lub lokalnie:
#   ./install.sh [--venv PATH] [--with-optional]
#
# Wynik: venv w ~/qsim-venv z zainstalowanym qsim + aliasy `qsim-demo` i `qsim-handoff-check`.

set -euo pipefail

VENV="${VENV:-$HOME/qsim-venv}"
WITH_OPTIONAL=0
REPO_URL="https://github.com/SyriusM/qsim.git"
CLONE_DIR="${CLONE_DIR:-$HOME/qsim}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --venv) VENV="$2"; shift 2 ;;
        --with-optional) WITH_OPTIONAL=1; shift ;;
        --clone-dir) CLONE_DIR="$2"; shift 2 ;;
        -h|--help)
            sed -n '2,10p' "$0"; exit 0 ;;
        *) echo "Nieznana opcja: $1"; exit 1 ;;
    esac
done

detect_distro() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        echo "${ID:-unknown}"
    else
        echo "unknown"
    fi
}

DISTRO="$(detect_distro)"
echo ">>> Wykryto dystrybucję: $DISTRO"

PYBIN=""
case "$DISTRO" in
    cachyos|arch|manjaro|endeavouros)
        if ! command -v python3 >/dev/null; then
            echo ">>> Brak python3 — wymagane: sudo pacman -S python python-pip git"
            exit 1
        fi
        PYBIN="$(command -v python3)"
        ;;
    debian|ubuntu|linuxmint)
        if command -v python3.12 >/dev/null; then
            PYBIN="$(command -v python3.12)"
        elif command -v python3.13 >/dev/null; then
            PYBIN="$(command -v python3.13)"
        else
            echo ">>> Debian/Ubuntu: brak python3.12+. Zainstaluj ręcznie:"
            echo "    sudo curl -fsSL https://packages.sury.org/python/README.txt | sudo bash -"
            echo "    sudo apt install -y python3.12 python3.12-venv git"
            echo "    ...albo użyj pyenv i ponów instalację."
            exit 1
        fi
        ;;
    *)
        if command -v python3 >/dev/null; then
            PYBIN="$(command -v python3)"
        else
            echo ">>> Brak python3 — zainstaluj ręcznie i ponów."
            exit 1
        fi
        ;;
esac

PYVER="$("$PYBIN" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
echo ">>> Python: $PYBIN ($PYVER)"

if ! "$PYBIN" -c 'import sys; exit(0 if sys.version_info >= (3,12) else 1)'; then
    echo ">>> WYMAGANY Python 3.12+. Masz $PYVER. Instalacja przerwana."
    exit 1
fi

if [[ ! -d "$CLONE_DIR/.git" ]]; then
    echo ">>> Klonuję $REPO_URL → $CLONE_DIR"
    git clone "$REPO_URL" "$CLONE_DIR"
else
    echo ">>> Repo już w $CLONE_DIR — pull"
    git -C "$CLONE_DIR" pull --ff-only
fi

if [[ ! -d "$VENV" ]]; then
    echo ">>> Tworzę venv: $VENV"
    "$PYBIN" -m venv "$VENV"
fi

PIP="$VENV/bin/pip"
"$PIP" install --upgrade pip wheel >/dev/null

echo ">>> Instaluję qsim"
if (( WITH_OPTIONAL )); then
    "$PIP" install -e "$CLONE_DIR[all]"
else
    "$PIP" install -e "$CLONE_DIR"
fi

MEMPALACE="${MEMPALACE_PATH:-$HOME/mempalace}"
if [[ ! -d "$MEMPALACE" ]]; then
    echo ""
    echo "!!! UWAGA: MemPalace nie znaleziony w $MEMPALACE"
    echo "    qsim potrzebuje bge-m3 embeddingów z MemPalace do działania ipq."
    echo "    Ustaw: export MEMPALACE_PATH=/ścieżka/do/mempalace"
    echo "    Lub sklonuj: https://github.com/SyriusM/mempalace"
fi

echo ""
echo ">>> Gotowe. Aktywuj venv i testuj:"
echo "    source $VENV/bin/activate          # bash/zsh"
echo "    source $VENV/bin/activate.fish     # fish"
echo "    qsim-handoff-check"
echo "    qsim-demo"
