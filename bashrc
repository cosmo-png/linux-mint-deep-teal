# Deep Teal rice: interactive Bash setup.

alias ll='ls -alF --color=auto'
alias la='ls -A --color=auto'
alias l='ls -CF --color=auto'
alias ..='cd ..'
alias ...='cd ../..'
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'

mkcd() {
    [[ $# -eq 1 ]] || { printf 'Usage: mkcd DIRECTORY\n' >&2; return 2; }
    mkdir -p -- "$1" && cd -- "$1"
}

extract() {
    [[ $# -eq 1 && -f "$1" ]] || { printf 'Usage: extract ARCHIVE\n' >&2; return 2; }
    case "$1" in
        *.tar.bz2|*.tbz2) tar -xjf -- "$1" ;;
        *.tar.gz|*.tgz)   tar -xzf -- "$1" ;;
        *.tar.xz|*.txz)   tar -xJf -- "$1" ;;
        *.tar)            tar -xf -- "$1" ;;
        *.bz2)             bunzip2 -- "$1" ;;
        *.gz)              gunzip -- "$1" ;;
        *.xz)              unxz -- "$1" ;;
        *.zip)             unzip -- "$1" ;;
        *) printf 'extract: unsupported archive: %s\n' "$1" >&2; return 1 ;;
    esac
}

if [[ -n "${BASH_VERSION:-}" ]]; then
    __deep_teal_git_branch() {
        command -v git >/dev/null 2>&1 || return
        git rev-parse --is-inside-work-tree >/dev/null 2>&1 || return
        local branch
        branch=$(git symbolic-ref --quiet --short HEAD 2>/dev/null) || \
            branch=$(git rev-parse --short HEAD 2>/dev/null) || return
        printf '  git:%s' "$branch"
    }
    PS1='\[\e[1;36m\]\u@\h\[\e[0m\] \[\e[1;34m\]\w\[\e[0;33m\]$(__deep_teal_git_branch)\[\e[0m\]\n\[\e[1;36m\]❯\[\e[0m\] '
fi
